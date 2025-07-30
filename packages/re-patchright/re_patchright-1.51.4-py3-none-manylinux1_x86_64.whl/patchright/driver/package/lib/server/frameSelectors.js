"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.FrameSelectors = void 0;
var _utils = require("../utils");
var _selectorParser = require("../utils/isomorphic/selectorParser");
var _dom = require("./dom");
/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

class FrameSelectors {
  constructor(frame) {
    this.frame = void 0;
    this.frame = frame;
  }
  _parseSelector(selector, options) {
    const strict = typeof options?.strict === 'boolean' ? options.strict : !!this.frame._page.context()._options.strictSelectors;
    return this.frame._page.context().selectors().parseSelector(selector, strict);
  }
  async query(selector, options, scope) {
    const resolved = await this.resolveInjectedForSelector(selector, options, scope);
    // Be careful, |this.frame| can be different from |resolved.frame|.
    if (!resolved) return null;
    const handle = await resolved.injected.evaluateHandle((injected, {
      info,
      scope
    }) => {
      return injected.querySelector(info.parsed, scope || document, info.strict);
    }, {
      info: resolved.info,
      scope: resolved.scope
    });
    const elementHandle = handle.asElement();
    if (!elementHandle) {
      handle.dispose();
      return null;
    }
    return adoptIfNeeded(elementHandle, await resolved.frame._mainContext());
  }
  async queryArrayInMainWorld(selector, scope) {
    // _debugLogger.debugLogger.log('api',`PVM14 queryArrayInMainWorld: selector=[${selector}] scope=[${scope}]...`);
    const resolved = await this.resolveInjectedForSelector(selector, {
      mainWorld: true
    }, scope);
    // Be careful, |this.frame| can be different from |resolved.frame|.
    if (!resolved) throw new Error(`Failed to find frame for selector "${selector}"`);
    // _debugLogger.debugLogger.log('api',
    //   `PVM14 queryArrayInMainWorld: resolved.info=[${JSON.stringify(resolved.info)}] resolved.scope=[${
    //     resolved.scope}] resolved.frame !== this.frame [${resolved.frame !== this.frame}] ...`);

    /* All this code below is needed because certain execution paths (e.g., 'all_inner_texts()' or 'element_handles()' invocations)
        get here and, in the case of existing closed shadow roots, just by inspecting what is in the 'resolved.frame'
        they wouldn't get all the elements. The real question is: WHY DIDN'T I HAVE TO IMPLEMENT THIS IN OTHER POINTS
        OF THIS FILE AS 'query', 'queryCount' OR 'queryAll' ?
        I think the response is that these functions aren't used anymore, but I'm not sure... */

    // Get JSHandles to all closed shadow roots first. These handles will be passed to the browser-side function.
    const closedShadowRootHandles = await resolved.frame.getClosedShadowRoots();
    // _debugLogger.debugLogger.log('api', `PVM14 queryArrayInMainWorld: Found ${closedShadowRootHandles.length} closed shadow roots.`);

    /* This function runs in the browser.
        argInitialScope is a DOM element (or document/null).
        argShadowRootDOMElements is an array of ShadowRoot DOM elements. */
    const pageFunction = (injected, {
      argInfo,
      argInitialScope,
      argShadowRootDOMElements
    }) => {
      const allFoundDOMElements = [];
      const parsedSelector = argInfo.parsed;

      /* 1. Query in the main document (or initial scope)
          'injected.querySelectorAll' returns a NodeList or similar array-like structure of DOM elements. */
      const mainDocNodeList = injected.querySelectorAll(parsedSelector, argInitialScope || document);
      for (let i = 0; i < mainDocNodeList.length; i++) {
        allFoundDOMElements.push(mainDocNodeList[i]);
      }
      // console.log(`PVM14 BROWSER: Found ${mainDocNodeList.length} elements in main/initial scope for selector:`, parsedSelector);

      /* TODO: PVM14 Ugly as hell. Tailor-made "if" designed to make locator "> *" work.
          The idea is—to avoid duplicates—not to check shadow roots if we are looking for "scope > *"
          unless we are dealing with the host of the shadowRoot (in that case, the direct children of the host
          are the shadowRoots and they must be inspected). */
      var firstSimple = parsedSelector?.parts?.[0]?.body?.[0]?.simples?.[0];
      var lookingForDirectChildElementsOfCurrentElement = firstSimple?.selector?.functions?.[0]?.name === "scope" && firstSimple?.combinator === ">";

      /* 2. Query in each closed shadow root
          argShadowRootDOMElements is an array of actual ShadowRoot DOM elements here. */
      for (const shadowRoot of argShadowRootDOMElements) {
        const isScopeTheHost = argInitialScope === shadowRoot.host;
        if (lookingForDirectChildElementsOfCurrentElement && !isScopeTheHost) {} else {
          const shadowNodeList = injected.querySelectorAll(parsedSelector, shadowRoot);
          for (let i = 0; i < shadowNodeList.length; i++) {
            allFoundDOMElements.push(shadowNodeList[i]);
          }
        }
        // console.log(`PVM14 BROWSER: Found ${shadowNodeList.length} elements in a shadow root for selector:`, parsedSelector);
      }
      // console.log(`PVM14 BROWSER: Total elements found: ${allFoundDOMElements.length}`);
      return allFoundDOMElements; // This will be an array of DOM elements
    };

    /* Execute the pageFunction in the browser.
        - resolved.injected is the InjectedScript instance for the correct context.
        - The second argument to evaluateHandle is an object containing arguments for pageFunction.
          JSHandles (like resolved.scope and elements of closedShadowRootHandles) passed here
          will be resolved to their corresponding DOM elements/values within pageFunction. */
    const finalArrayHandle = await resolved.injected.evaluateHandle(pageFunction, {
      // Argument for pageFunction
      argInfo: resolved.info,
      argInitialScope: resolved.scope,
      // JSHandle, resolves to DOM element/null in pageFunction
      argShadowRootDOMElements: closedShadowRootHandles // Array of JSHandles, resolves to array of ShadowRoot DOM elements
    });

    /* Dispose the JSHandles for the shadow roots now that they've been used
        and their corresponding DOM elements have been processed by pageFunction. */
    for (const handle of closedShadowRootHandles) {
      await handle.dispose();
    }
    // _debugLogger.debugLogger.log('api', `PVM14 queryArrayInMainWorld: Disposed ${closedShadowRootHandles.length} closed shadow root JSHandles.`);

    return finalArrayHandle;
  }
  async queryCount(selector) {
    const resolved = await this.resolveInjectedForSelector(selector);
    // Be careful, |this.frame| can be different from |resolved.frame|.
    if (!resolved) throw new Error(`Failed to find frame for selector "${selector}"`);
    return await resolved.injected.evaluate((injected, {
      info
    }) => {
      return injected.querySelectorAll(info.parsed, document).length;
    }, {
      info: resolved.info
    });
  }
  async queryAll(selector, scope) {
    const resolved = await this.resolveInjectedForSelector(selector, {}, scope);
    // Be careful, |this.frame| can be different from |resolved.frame|.
    if (!resolved) return [];
    const arrayHandle = await resolved.injected.evaluateHandle((injected, {
      info,
      scope
    }) => {
      return injected.querySelectorAll(info.parsed, scope || document);
    }, {
      info: resolved.info,
      scope: resolved.scope
    });
    const properties = await arrayHandle.getProperties();
    arrayHandle.dispose();

    // Note: adopting elements one by one may be slow. If we encounter the issue here,
    // we might introduce 'useMainContext' option or similar to speed things up.
    const targetContext = await resolved.frame._mainContext();
    const result = [];
    for (const property of properties.values()) {
      const elementHandle = property.asElement();
      if (elementHandle) result.push(adoptIfNeeded(elementHandle, targetContext));else property.dispose();
    }
    return Promise.all(result);
  }
  async resolveFrameForSelector(selector, options = {}, scope) {
    let frame = this.frame;
    const frameChunks = (0, _selectorParser.splitSelectorByFrame)(selector);
    for (const chunk of frameChunks) {
      (0, _selectorParser.visitAllSelectorParts)(chunk, (part, nested) => {
        if (nested && part.name === 'internal:control' && part.body === 'enter-frame') {
          const locator = (0, _utils.asLocator)(this.frame._page.attribution.playwright.options.sdkLanguage, selector);
          throw new _selectorParser.InvalidSelectorError(`Frame locators are not allowed inside composite locators, while querying "${locator}"`);
        }
      });
    }
    for (let i = 0; i < frameChunks.length - 1; ++i) {
      const info = this._parseSelector(frameChunks[i], options);
      const context = await frame._context(info.world);
      const injectedScript = await context.injectedScript();
      const handle = await injectedScript.evaluateHandle((injected, {
        info,
        scope,
        selectorString
      }) => {
        const element = injected.querySelector(info.parsed, scope || document, info.strict);
        if (element && element.nodeName !== 'IFRAME' && element.nodeName !== 'FRAME') throw injected.createStacklessError(`Selector "${selectorString}" resolved to ${injected.previewNode(element)}, <iframe> was expected`);
        return element;
      }, {
        info,
        scope: i === 0 ? scope : undefined,
        selectorString: (0, _selectorParser.stringifySelector)(info.parsed)
      });
      let element = handle.asElement();
      if (!element)
        // My modification: instead of giving up, look for the frame in closed shadowRoot objects
        element = await this.lookForFrameInClosedShadowRoots(frame, injectedScript, info, (0, _selectorParser.stringifySelector)(info.parsed));
      if (!element) return null;
      const maybeFrame = await frame._page._delegate.getContentFrame(element);
      element.dispose();
      if (!maybeFrame) return null;
      frame = maybeFrame;
    }
    // If we end up in the different frame, we should start from the frame root, so throw away the scope.
    if (frame !== this.frame) scope = undefined;
    return {
      frame,
      info: frame.selectors._parseSelector(frameChunks[frameChunks.length - 1], options),
      scope
    };
  }
  async resolveInjectedForSelector(selector, options, scope) {
    const resolved = await this.resolveFrameForSelector(selector, options, scope);
    // Be careful, |this.frame| can be different from |resolved.frame|.
    if (!resolved) return;
    const context = await resolved.frame._context(options?.mainWorld ? 'main' : resolved.info.world);
    const injected = await context.injectedScript();
    return {
      injected,
      info: resolved.info,
      frame: resolved.frame,
      scope: resolved.scope
    };
  }
  async lookForFrameInClosedShadowRoots(frame, injectedScript, info, selectorString) {
    const closedShadowRoots = await frame.getClosedShadowRoots();
    const elements = [];
    for (const shadowRootHandle of closedShadowRoots) {
      const handle = await injectedScript.evaluateHandle((remoteInjectedScript, {
        info,
        scope,
        selectorString
      }) => {
        const element = remoteInjectedScript.querySelector(info.parsed, scope, info.strict);
        if (element && element.nodeName !== 'IFRAME' && element.nodeName !== 'FRAME') throw remoteInjectedScript.createStacklessError(`Selector "${selectorString}" resolved to ${remoteInjectedScript.previewNode(element)}, <iframe> was expected`);
        return element;
      }, {
        info,
        scope: shadowRootHandle,
        selectorString
      });
      const element = handle.asElement();
      if (element) elements.push(element);
      // Getting rid of the shadowRootHandle after using it to avoid creating memory leaks ...
      await shadowRootHandle.dispose();
    }
    if (elements.length > 1) {
      // We throw a NonRecoverableDOMError indicating multiple frames found within closed shadow roots.
      // I'm not sure if this is really an error but I want to see it when it happens and I want it to stop the execution ...
      const elementsPreview = elements.map(e => e.toString()).join(', ');
      throw new _dom.NonRecoverableDOMError(`Selector "${selectorString}" resolved to ${elements.length} elements in closed shadow roots: [${elementsPreview}]. Expected 1 frame element.`);
    }

    // Return the single element found, or null if none were found.
    return elements.length === 1 ? elements[0] : null;
  }
}
exports.FrameSelectors = FrameSelectors;
async function adoptIfNeeded(handle, context) {
  if (handle._context === context) return handle;
  const adopted = await handle._page._delegate.adoptElementHandle(handle, context);
  handle.dispose();
  return adopted;
}