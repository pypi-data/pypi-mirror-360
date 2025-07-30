"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var frameSelectors_exports = {};
__export(frameSelectors_exports, {
  FrameSelectors: () => FrameSelectors
});
module.exports = __toCommonJS(frameSelectors_exports);
var import_utils = require("../utils");
var import_selectorParser = require("../utils/isomorphic/selectorParser");
var import_dom = require("./dom");
class FrameSelectors {
  constructor(frame) {
    this.frame = frame;
  }
  _parseSelector(selector, options) {
    const strict = typeof options?.strict === "boolean" ? options.strict : !!this.frame._page.context()._options.strictSelectors;
    return this.frame._page.context().selectors().parseSelector(selector, strict);
  }
  async query(selector, options, scope) {
    const resolved = await this.resolveInjectedForSelector(selector, options, scope);
    if (!resolved)
      return null;
    const handle = await resolved.injected.evaluateHandle((injected, { info, scope: scope2 }) => {
      return injected.querySelector(info.parsed, scope2 || document, info.strict);
    }, { info: resolved.info, scope: resolved.scope });
    const elementHandle = handle.asElement();
    if (!elementHandle) {
      handle.dispose();
      return null;
    }
    return adoptIfNeeded(elementHandle, await resolved.frame._mainContext());
  }
  async queryArrayInMainWorld(selector, scope, isolatedContext) {
    const resolved = await this.resolveInjectedForSelector(selector, { mainWorld: !isolatedContext }, scope);
    if (!resolved) throw new Error(`Failed to find frame for selector "${selector}"`);
    const closedShadowRootHandles = await resolved.frame.getClosedShadowRoots();
    const pageFunction = (injected, { argInfo, argInitialScope, argShadowRootDOMElements }) => {
      const allFoundDOMElements = [];
      const parsedSelector = argInfo.parsed;
      const mainDocNodeList = injected.querySelectorAll(parsedSelector, argInitialScope || document);
      for (let i = 0; i < mainDocNodeList.length; i++) {
        allFoundDOMElements.push(mainDocNodeList[i]);
      }
      var firstSimple = parsedSelector?.parts?.[0]?.body?.[0]?.simples?.[0];
      var lookingForDirectChildElementsOfCurrentElement = firstSimple?.selector?.functions?.[0]?.name === "scope" && firstSimple?.combinator === ">";
      for (const shadowRoot of argShadowRootDOMElements) {
        const isScopeTheHost = argInitialScope === shadowRoot.host;
        if (lookingForDirectChildElementsOfCurrentElement && !isScopeTheHost) {
        } else {
          const shadowNodeList = injected.querySelectorAll(parsedSelector, shadowRoot);
          for (let i = 0; i < shadowNodeList.length; i++) {
            allFoundDOMElements.push(shadowNodeList[i]);
          }
        }
      }
      return allFoundDOMElements;
    };
    const finalArrayHandle = await resolved.injected.evaluateHandle(
      pageFunction,
      {
        // Argument for pageFunction
        argInfo: resolved.info,
        argInitialScope: resolved.scope,
        // JSHandle, resolves to DOM element/null in pageFunction
        argShadowRootDOMElements: closedShadowRootHandles
        // Array of JSHandles, resolves to array of ShadowRoot DOM elements
      }
    );
    for (const handle of closedShadowRootHandles) {
      await handle.dispose();
    }
    return finalArrayHandle;
  }
  async queryCount(selector) {
    const resolved = await this.resolveInjectedForSelector(selector);
    if (!resolved)
      throw new Error(`Failed to find frame for selector "${selector}"`);
    return await resolved.injected.evaluate((injected, { info }) => {
      return injected.querySelectorAll(info.parsed, document).length;
    }, { info: resolved.info });
  }
  async queryAll(selector, scope) {
    const resolved = await this.resolveInjectedForSelector(selector, {}, scope);
    if (!resolved)
      return [];
    const arrayHandle = await resolved.injected.evaluateHandle((injected, { info, scope: scope2 }) => {
      return injected.querySelectorAll(info.parsed, scope2 || document);
    }, { info: resolved.info, scope: resolved.scope });
    const properties = await arrayHandle.getProperties();
    arrayHandle.dispose();
    const targetContext = await resolved.frame._mainContext();
    const result = [];
    for (const property of properties.values()) {
      const elementHandle = property.asElement();
      if (elementHandle)
        result.push(adoptIfNeeded(elementHandle, targetContext));
      else
        property.dispose();
    }
    return Promise.all(result);
  }
  async resolveFrameForSelector(selector, options = {}, scope) {
    let frame = this.frame;
    const frameChunks = (0, import_selectorParser.splitSelectorByFrame)(selector);
    for (const chunk of frameChunks) {
      (0, import_selectorParser.visitAllSelectorParts)(chunk, (part, nested) => {
        if (nested && part.name === "internal:control" && part.body === "enter-frame") {
          const locator = (0, import_utils.asLocator)(this.frame._page.attribution.playwright.options.sdkLanguage, selector);
          throw new import_selectorParser.InvalidSelectorError(`Frame locators are not allowed inside composite locators, while querying "${locator}"`);
        }
      });
    }
    for (let i = 0; i < frameChunks.length - 1; ++i) {
      const info = this._parseSelector(frameChunks[i], options);
      const context = await frame._context(info.world);
      const injectedScript = await context.injectedScript();
      const handle = await injectedScript.evaluateHandle((injected, { info: info2, scope: scope2, selectorString }) => {
        const element2 = injected.querySelector(info2.parsed, scope2 || document, info2.strict);
        if (element2 && element2.nodeName !== "IFRAME" && element2.nodeName !== "FRAME")
          throw injected.createStacklessError(`Selector "${selectorString}" resolved to ${injected.previewNode(element2)}, <iframe> was expected`);
        return element2;
      }, { info, scope: i === 0 ? scope : void 0, selectorString: (0, import_selectorParser.stringifySelector)(info.parsed) });
      let element = handle.asElement();
      if (!element)
        element = await this.lookForFrameInClosedShadowRoots(frame, injectedScript, info, (0, import_selectorParser.stringifySelector)(info.parsed));
      if (!element) return null;
      const maybeFrame = await frame._page._delegate.getContentFrame(element);
      element.dispose();
      if (!maybeFrame)
        return null;
      frame = maybeFrame;
    }
    if (frame !== this.frame)
      scope = void 0;
    return { frame, info: frame.selectors._parseSelector(frameChunks[frameChunks.length - 1], options), scope };
  }
  async resolveInjectedForSelector(selector, options, scope) {
    const resolved = await this.resolveFrameForSelector(selector, options, scope);
    if (!resolved)
      return;
    const context = await resolved.frame._context(options?.mainWorld ? "main" : resolved.info.world);
    const injected = await context.injectedScript();
    return { injected, info: resolved.info, frame: resolved.frame, scope: resolved.scope };
  }
  async _customFindFramesByParsed(injected, client, context, documentScope, parsed) {
    var parsedEdits = { ...parsed };
    var currentScopingElements = [documentScope];
    while (parsed.parts.length > 0) {
      var part = parsed.parts.shift();
      parsedEdits.parts = [part];
      var elements = [];
      var elementsIndexes = [];
      if (part.name == "nth") {
        const partNth = Number(part.body);
        if (partNth > currentScopingElements.length || partNth < -currentScopingElements.length) {
          return continuePolling;
        } else {
          currentScopingElements = [currentScopingElements.at(partNth)];
          continue;
        }
      } else if (part.name == "internal:or") {
        var orredElements = await this._customFindFramesByParsed(injected, client, context, documentScope, part.body.parsed);
        elements = currentScopingElements.concat(orredElements);
      } else if (part.name == "internal:and") {
        var andedElements = await this._customFindFramesByParsed(injected, client, context, documentScope, part.body.parsed);
        const backendNodeIds = new Set(andedElements.map((item) => item.backendNodeId));
        elements = currentScopingElements.filter((item) => backendNodeIds.has(item.backendNodeId));
      } else {
        for (const scope of currentScopingElements) {
          const describedScope = await client.send("DOM.describeNode", {
            objectId: scope._objectId,
            depth: -1,
            pierce: true
          });
          var queryingElements = [];
          let findClosedShadowRoots2 = function(node, results = []) {
            if (!node || typeof node !== "object") return results;
            if (node.shadowRoots && Array.isArray(node.shadowRoots)) {
              for (const shadowRoot2 of node.shadowRoots) {
                if (shadowRoot2.shadowRootType === "closed" && shadowRoot2.backendNodeId) {
                  results.push(shadowRoot2.backendNodeId);
                }
                findClosedShadowRoots2(shadowRoot2, results);
              }
            }
            if (node.nodeName !== "IFRAME" && node.children && Array.isArray(node.children)) {
              for (const child of node.children) {
                findClosedShadowRoots2(child, results);
              }
            }
            return results;
          };
          var findClosedShadowRoots = findClosedShadowRoots2;
          var shadowRootBackendIds = findClosedShadowRoots2(describedScope.node);
          var shadowRoots = [];
          for (var shadowRootBackendId of shadowRootBackendIds) {
            var resolvedShadowRoot = await client.send("DOM.resolveNode", {
              backendNodeId: shadowRootBackendId,
              contextId: context.delegate._contextId
            });
            shadowRoots.push(new ElementHandle(context, resolvedShadowRoot.object.objectId));
          }
          for (var shadowRoot of shadowRoots) {
            const shadowElements = await shadowRoot.evaluateHandleInUtility(([injected2, node, { parsed: parsed2 }]) => {
              const elements2 = injected2.querySelectorAll(parsed2, node);
              return elements2;
            }, {
              parsed: parsedEdits
            });
            const shadowElementsAmount = await shadowElements.getProperty("length");
            queryingElements.push([shadowElements, shadowElementsAmount, shadowRoot]);
          }
          const rootElements = await scope.evaluateHandleInUtility(([injected2, node, { parsed: parsed2 }]) => {
            const elements2 = injected2.querySelectorAll(parsed2, node);
            return elements2;
          }, {
            parsed: parsedEdits
          });
          const rootElementsAmount = await rootElements.getProperty("length");
          queryingElements.push([rootElements, rootElementsAmount, injected]);
          for (var queryedElement of queryingElements) {
            var elementsToCheck = queryedElement[0];
            var elementsAmount = await queryedElement[1].jsonValue();
            var parentNode = queryedElement[2];
            for (var i = 0; i < elementsAmount; i++) {
              if (parentNode.constructor.name == "ElementHandle") {
                var elementToCheck = await parentNode.evaluateHandleInUtility(([injected2, node, { index, elementsToCheck: elementsToCheck2 }]) => {
                  return elementsToCheck2[index];
                }, { index: i, elementsToCheck });
              } else {
                var elementToCheck = await parentNode.evaluateHandle((injected2, { index, elementsToCheck: elementsToCheck2 }) => {
                  return elementsToCheck2[index];
                }, { index: i, elementsToCheck });
              }
              elementToCheck.parentNode = parentNode;
              var resolvedElement = await client.send("DOM.describeNode", {
                objectId: elementToCheck._objectId,
                depth: -1
              });
              elementToCheck.backendNodeId = resolvedElement.node.backendNodeId;
              elements.push(elementToCheck);
            }
          }
        }
      }
      currentScopingElements = [];
      for (var element of elements) {
        var elemIndex = element.backendNodeId;
        var elemPos = elementsIndexes.findIndex((index) => index > elemIndex);
        if (elemPos === -1) {
          currentScopingElements.push(element);
          elementsIndexes.push(elemIndex);
        } else {
          currentScopingElements.splice(elemPos, 0, element);
          elementsIndexes.splice(elemPos, 0, elemIndex);
        }
      }
    }
    return currentScopingElements;
  }
  async lookForFrameInClosedShadowRoots(frame, injectedScript, info, selectorString) {
    const closedShadowRoots = await frame.getClosedShadowRoots();
    const elements = [];
    for (const shadowRootHandle of closedShadowRoots) {
      const handle = await injectedScript.evaluateHandle((remoteInjectedScript, {
        info: info2,
        scope,
        selectorString: selectorString2
      }) => {
        const element2 = remoteInjectedScript.querySelector(info2.parsed, scope, info2.strict);
        if (element2 && element2.nodeName !== "IFRAME" && element2.nodeName !== "FRAME")
          throw remoteInjectedScript.createStacklessError(`Selector "${selectorString2}" resolved to ${remoteInjectedScript.previewNode(element2)}, <iframe> was expected`);
        return element2;
      }, {
        info,
        scope: shadowRootHandle,
        selectorString
      });
      const element = handle.asElement();
      if (element) elements.push(element);
      await shadowRootHandle.dispose();
    }
    if (elements.length > 1) {
      const elementsPreview = elements.map((e) => e.toString()).join(", ");
      throw new import_dom.NonRecoverableDOMError(`Selector "${selectorString}" resolved to ${elements.length} elements in closed shadow roots: [${elementsPreview}]. Expected 1 frame element.`);
    }
    return elements.length === 1 ? elements[0] : null;
  }
}
async function adoptIfNeeded(handle, context) {
  if (handle._context === context)
    return handle;
  const adopted = await handle._page._delegate.adoptElementHandle(handle, context);
  handle.dispose();
  return adopted;
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  FrameSelectors
});
