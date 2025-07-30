"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.CRNetworkManager = void 0;
var _crypto = _interopRequireDefault(require("crypto"));
var _utils = require("../../utils");
var _eventsHelper = require("../utils/eventsHelper");
var _helper = require("../helper");
var network = _interopRequireWildcard(require("../network"));
var _protocolError = require("../protocolError");
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function (e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { default: e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && {}.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n.default = e, t && t.set(e, n), n; }
function _interopRequireDefault(e) { return e && e.__esModule ? e : { default: e }; }
// undetected-undetected_playwright-patch - custom imports

/**
 * Copyright 2017 Google Inc. All rights reserved.
 * Modifications copyright (c) Microsoft Corporation.
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

class CRNetworkManager {
  constructor(page, serviceWorker) {
    this._page = void 0;
    this._serviceWorker = void 0;
    this._requestIdToRequest = new Map();
    this._requestIdToRequestWillBeSentEvent = new Map();
    this._credentials = null;
    this._attemptedAuthentications = new Set();
    this._userRequestInterceptionEnabled = false;
    this._protocolRequestInterceptionEnabled = false;
    this._offline = false;
    this._extraHTTPHeaders = [];
    this._requestIdToRequestPausedEvent = new Map();
    this._responseExtraInfoTracker = new ResponseExtraInfoTracker();
    this._sessions = new Map();
    this._alreadyTrackedNetworkIds = new Set();
    this._page = page;
    this._serviceWorker = serviceWorker;
  }
  async addSession(session, workerFrame, isMain) {
    const sessionInfo = {
      session,
      isMain,
      workerFrame,
      eventListeners: []
    };
    sessionInfo.eventListeners = [_eventsHelper.eventsHelper.addEventListener(session, 'Fetch.requestPaused', this._onRequestPaused.bind(this, sessionInfo)), _eventsHelper.eventsHelper.addEventListener(session, 'Fetch.authRequired', this._onAuthRequired.bind(this, sessionInfo)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.requestWillBeSent', this._onRequestWillBeSent.bind(this, sessionInfo)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.requestWillBeSentExtraInfo', this._onRequestWillBeSentExtraInfo.bind(this)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.requestServedFromCache', this._onRequestServedFromCache.bind(this)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.responseReceived', this._onResponseReceived.bind(this, sessionInfo)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.responseReceivedExtraInfo', this._onResponseReceivedExtraInfo.bind(this)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.loadingFinished', this._onLoadingFinished.bind(this, sessionInfo)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.loadingFailed', this._onLoadingFailed.bind(this, sessionInfo))];
    if (this._page) {
      sessionInfo.eventListeners.push(...[_eventsHelper.eventsHelper.addEventListener(session, 'Network.webSocketCreated', e => this._page._frameManager.onWebSocketCreated(e.requestId, e.url)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.webSocketWillSendHandshakeRequest', e => this._page._frameManager.onWebSocketRequest(e.requestId)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.webSocketHandshakeResponseReceived', e => this._page._frameManager.onWebSocketResponse(e.requestId, e.response.status, e.response.statusText)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.webSocketFrameSent', e => e.response.payloadData && this._page._frameManager.onWebSocketFrameSent(e.requestId, e.response.opcode, e.response.payloadData)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.webSocketFrameReceived', e => e.response.payloadData && this._page._frameManager.webSocketFrameReceived(e.requestId, e.response.opcode, e.response.payloadData)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.webSocketClosed', e => this._page._frameManager.webSocketClosed(e.requestId)), _eventsHelper.eventsHelper.addEventListener(session, 'Network.webSocketFrameError', e => this._page._frameManager.webSocketError(e.requestId, e.errorMessage))]);
    }
    this._sessions.set(session, sessionInfo);
    await Promise.all([session.send('Network.enable'), this._updateProtocolRequestInterceptionForSession(sessionInfo, true /* initial */), this._setOfflineForSession(sessionInfo, true /* initial */), this._setExtraHTTPHeadersForSession(sessionInfo, true /* initial */)]);
  }
  removeSession(session) {
    const info = this._sessions.get(session);
    if (info) _eventsHelper.eventsHelper.removeEventListeners(info.eventListeners);
    this._sessions.delete(session);
  }
  async _forEachSession(cb) {
    await Promise.all([...this._sessions.values()].map(info => {
      if (info.isMain) return cb(info);
      return cb(info).catch(e => {
        // Broadcasting a message to the closed target should be a noop.
        if ((0, _protocolError.isSessionClosedError)(e)) return;
        throw e;
      });
    }));
  }
  async authenticate(credentials) {
    this._credentials = credentials;
    await this._updateProtocolRequestInterception();
  }
  async setOffline(offline) {
    if (offline === this._offline) return;
    this._offline = offline;
    await this._forEachSession(info => this._setOfflineForSession(info));
  }
  async _setOfflineForSession(info, initial) {
    if (initial && !this._offline) return;
    // Workers are affected by the owner frame's Network.emulateNetworkConditions.
    if (info.workerFrame) return;
    await info.session.send('Network.emulateNetworkConditions', {
      offline: this._offline,
      // values of 0 remove any active throttling. crbug.com/456324#c9
      latency: 0,
      downloadThroughput: -1,
      uploadThroughput: -1
    });
  }
  async setRequestInterception(value) {
    this._userRequestInterceptionEnabled = value;
    await this._updateProtocolRequestInterception();
  }
  async _updateProtocolRequestInterception() {
    const enabled = this._userRequestInterceptionEnabled || !!this._credentials;
    if (enabled === this._protocolRequestInterceptionEnabled) return;
    this._protocolRequestInterceptionEnabled = enabled;
    await this._forEachSession(info => this._updateProtocolRequestInterceptionForSession(info));
  }
  async _updateProtocolRequestInterceptionForSession(info, initial) {
    const enabled = this._protocolRequestInterceptionEnabled;
    if (initial && !enabled) return;
    const cachePromise = info.session.send('Network.setCacheDisabled', {
      cacheDisabled: false
    });
    let fetchPromise = Promise.resolve(undefined);
    if (!info.workerFrame) {
      if (enabled) fetchPromise = info.session.send('Fetch.enable', {
        handleAuthRequests: true,
        patterns: [{
          urlPattern: '*',
          requestStage: 'Request'
        }]
      });else fetchPromise = info.session.send('Fetch.disable');
    }
    await Promise.all([cachePromise, fetchPromise]);
  }
  async setExtraHTTPHeaders(extraHTTPHeaders) {
    if (!this._extraHTTPHeaders.length && !extraHTTPHeaders.length) return;
    this._extraHTTPHeaders = extraHTTPHeaders;
    await this._forEachSession(info => this._setExtraHTTPHeadersForSession(info));
  }
  async _setExtraHTTPHeadersForSession(info, initial) {
    if (initial && !this._extraHTTPHeaders.length) return;
    await info.session.send('Network.setExtraHTTPHeaders', {
      headers: (0, _utils.headersArrayToObject)(this._extraHTTPHeaders, false /* lowerCase */)
    });
  }
  async clearCache() {
    await this._forEachSession(async info => {
      // Sending 'Network.setCacheDisabled' with 'cacheDisabled = true' will clear the MemoryCache.
      await info.session.send('Network.setCacheDisabled', {
        cacheDisabled: true
      });
      if (!this._protocolRequestInterceptionEnabled) await info.session.send('Network.setCacheDisabled', {
        cacheDisabled: false
      });
      if (!info.workerFrame) await info.session.send('Network.clearBrowserCache');
    });
  }
  _onRequestWillBeSent(sessionInfo, event) {
    // Request interception doesn't happen for data URLs with Network Service.
    if (this._protocolRequestInterceptionEnabled && !event.request.url.startsWith('data:')) {
      const requestId = event.requestId;
      const requestPausedEvent = this._requestIdToRequestPausedEvent.get(requestId);
      if (requestPausedEvent) {
        this._onRequest(sessionInfo, event, requestPausedEvent.sessionInfo, requestPausedEvent.event);
        this._requestIdToRequestPausedEvent.delete(requestId);
      } else {
        this._requestIdToRequestWillBeSentEvent.set(event.requestId, {
          sessionInfo,
          event
        });
      }
    } else {
      this._onRequest(sessionInfo, event, undefined, undefined);
    }
  }
  _onRequestServedFromCache(event) {
    this._responseExtraInfoTracker.requestServedFromCache(event);
  }
  _onRequestWillBeSentExtraInfo(event) {
    this._responseExtraInfoTracker.requestWillBeSentExtraInfo(event);
  }
  _onAuthRequired(sessionInfo, event) {
    let response = 'Default';
    const shouldProvideCredentials = this._shouldProvideCredentials(event.request.url);
    if (this._attemptedAuthentications.has(event.requestId)) {
      response = 'CancelAuth';
    } else if (shouldProvideCredentials) {
      response = 'ProvideCredentials';
      this._attemptedAuthentications.add(event.requestId);
    }
    const {
      username,
      password
    } = shouldProvideCredentials && this._credentials ? this._credentials : {
      username: undefined,
      password: undefined
    };
    sessionInfo.session._sendMayFail('Fetch.continueWithAuth', {
      requestId: event.requestId,
      authChallengeResponse: {
        response,
        username,
        password
      }
    });
  }
  _shouldProvideCredentials(url) {
    if (!this._credentials) return false;
    return !this._credentials.origin || new URL(url).origin.toLowerCase() === this._credentials.origin.toLowerCase();
  }
  _onRequestPaused(sessionInfo, event) {
    if (this._alreadyTrackedNetworkIds.has(event.networkId)) return;
    if (!event.networkId) {
      // Fetch without networkId means that request was not recognized by inspector, and
      // it will never receive Network.requestWillBeSent. Continue the request to not affect it.
      sessionInfo.session._sendMayFail('Fetch.continueRequest', {
        requestId: event.requestId
      });
      return;
    }
    if (event.request.url.startsWith('data:')) return;
    const requestId = event.networkId;
    const requestWillBeSentEvent = this._requestIdToRequestWillBeSentEvent.get(requestId);
    if (requestWillBeSentEvent) {
      this._onRequest(requestWillBeSentEvent.sessionInfo, requestWillBeSentEvent.event, sessionInfo, event);
      this._requestIdToRequestWillBeSentEvent.delete(requestId);
    } else {
      const existingRequest = this._requestIdToRequest.get(requestId);
      const alreadyContinuedParams = existingRequest?._route?._alreadyContinuedParams;
      if (alreadyContinuedParams && !event.redirectedRequestId) {
        // Sometimes Chromium network stack restarts the request internally.
        // For example, when no-cors request hits a "less public address space", it should be resent with cors.
        // There are some more examples here: https://source.chromium.org/chromium/chromium/src/+/main:services/network/url_loader.cc;l=1205-1234;drc=d5dd931e0ad3d9ffe74888ec62a3cc106efd7ea6
        // There are probably even more cases deep inside the network stack.
        //
        // Anyway, in this case, continue the request in the same way as before, and it should go through.
        //
        // Note: make sure not to prematurely continue the redirect, which shares the
        // `networkId` between the original request and the redirect.
        sessionInfo.session._sendMayFail('Fetch.continueRequest', {
          ...alreadyContinuedParams,
          requestId: event.requestId
        });
        return;
      }
      this._requestIdToRequestPausedEvent.set(requestId, {
        sessionInfo,
        event
      });
    }
  }
  _onRequest(requestWillBeSentSessionInfo, requestWillBeSentEvent, requestPausedSessionInfo, requestPausedEvent) {
    if (this._alreadyTrackedNetworkIds.has(requestWillBeSentEvent.initiator.requestId)) return;
    if (requestWillBeSentEvent.request.url.startsWith('data:')) return;
    let redirectedFrom = null;
    if (requestWillBeSentEvent.redirectResponse) {
      const request = this._requestIdToRequest.get(requestWillBeSentEvent.requestId);
      // If we connect late to the target, we could have missed the requestWillBeSent event.
      if (request) {
        this._handleRequestRedirect(request, requestWillBeSentEvent.redirectResponse, requestWillBeSentEvent.timestamp, requestWillBeSentEvent.redirectHasExtraInfo);
        redirectedFrom = request;
      }
    }
    let frame = requestWillBeSentEvent.frameId ? this._page?._frameManager.frame(requestWillBeSentEvent.frameId) : requestWillBeSentSessionInfo.workerFrame;
    // Requests from workers lack frameId, because we receive Network.requestWillBeSent
    // on the worker target. However, we receive Fetch.requestPaused on the page target,
    // and lack workerFrame there. Luckily, Fetch.requestPaused provides a frameId.
    if (!frame && this._page && requestPausedEvent && requestPausedEvent.frameId) frame = this._page._frameManager.frame(requestPausedEvent.frameId);

    // Check if it's main resource request interception (targetId === main frame id).
    if (!frame && this._page && requestWillBeSentEvent.frameId === (this._page?._delegate)._targetId) {
      // Main resource request for the page is being intercepted so the Frame is not created
      // yet. Precreate it here for the purposes of request interception. It will be updated
      // later as soon as the request continues and we receive frame tree from the page.
      frame = this._page._frameManager.frameAttached(requestWillBeSentEvent.frameId, null);
    }

    // CORS options preflight request is generated by the network stack. If interception is enabled,
    // we accept all CORS options, assuming that this was intended when setting route.
    //
    // Note: it would be better to match the URL against interception patterns.
    const isInterceptedOptionsPreflight = !!requestPausedEvent && requestPausedEvent.request.method === 'OPTIONS' && requestWillBeSentEvent.initiator.type === 'preflight';
    if (isInterceptedOptionsPreflight && (this._page || this._serviceWorker).needsRequestInterception()) {
      const requestHeaders = requestPausedEvent.request.headers;
      const responseHeaders = [{
        name: 'Access-Control-Allow-Origin',
        value: requestHeaders['Origin'] || '*'
      }, {
        name: 'Access-Control-Allow-Methods',
        value: requestHeaders['Access-Control-Request-Method'] || 'GET, POST, OPTIONS, DELETE'
      }, {
        name: 'Access-Control-Allow-Credentials',
        value: 'true'
      }];
      if (requestHeaders['Access-Control-Request-Headers']) responseHeaders.push({
        name: 'Access-Control-Allow-Headers',
        value: requestHeaders['Access-Control-Request-Headers']
      });
      requestPausedSessionInfo.session._sendMayFail('Fetch.fulfillRequest', {
        requestId: requestPausedEvent.requestId,
        responseCode: 204,
        responsePhrase: network.statusText(204),
        responseHeaders,
        body: ''
      });
      return;
    }

    // Non-service-worker requests MUST have a frame—if they don't, we pretend there was no request
    if (!frame && !this._serviceWorker) {
      if (requestPausedEvent) requestPausedSessionInfo.session._sendMayFail('Fetch.continueRequest', {
        requestId: requestPausedEvent.requestId
      });
      return;
    }
    let route = null;
    let headersOverride;
    if (requestPausedEvent) {
      // We do not support intercepting redirects.
      if (redirectedFrom || !this._userRequestInterceptionEnabled && this._protocolRequestInterceptionEnabled) {
        // Chromium does not preserve header overrides between redirects, so we have to do it ourselves.
        headersOverride = redirectedFrom?._originalRequestRoute?._alreadyContinuedParams?.headers;
        requestPausedSessionInfo.session._sendMayFail('Fetch.continueRequest', {
          requestId: requestPausedEvent.requestId,
          headers: headersOverride
        });
      } else {
        route = new RouteImpl(requestPausedSessionInfo.session, requestPausedEvent.requestId, this._page, requestPausedEvent.networkId, this);
      }
    }
    const isNavigationRequest = requestWillBeSentEvent.requestId === requestWillBeSentEvent.loaderId && requestWillBeSentEvent.type === 'Document';
    const documentId = isNavigationRequest ? requestWillBeSentEvent.loaderId : undefined;
    const request = new InterceptableRequest({
      session: requestWillBeSentSessionInfo.session,
      context: (this._page || this._serviceWorker)._browserContext,
      frame: frame || null,
      serviceWorker: this._serviceWorker || null,
      documentId,
      route,
      requestWillBeSentEvent,
      requestPausedEvent,
      redirectedFrom,
      headersOverride: headersOverride || null
    });
    this._requestIdToRequest.set(requestWillBeSentEvent.requestId, request);
    if (route) {
      // We may not receive extra info when intercepting the request.
      // Use the headers from the Fetch.requestPausedPayload and release the allHeaders()
      // right away, so that client can call it from the route handler.
      request.request.setRawRequestHeaders((0, _utils.headersObjectToArray)(requestPausedEvent.request.headers, '\n'));
    }
    (this._page?._frameManager || this._serviceWorker).requestStarted(request.request, route || undefined);
  }
  _createResponse(request, responsePayload, hasExtraInfo) {
    const getResponseBody = async () => {
      const contentLengthHeader = Object.entries(responsePayload.headers).find(header => header[0].toLowerCase() === 'content-length');
      const expectedLength = contentLengthHeader ? +contentLengthHeader[1] : undefined;
      const session = request.session;
      const response = await session.send('Network.getResponseBody', {
        requestId: request._requestId
      });
      if (response.body || !expectedLength) return Buffer.from(response.body, response.base64Encoded ? 'base64' : 'utf8');

      // Make sure no network requests sent while reading the body for fulfilled requests.
      if (request._route?._fulfilled) return Buffer.from('');

      // For <link prefetch we are going to receive empty body with non-empty content-length expectation. Reach out for the actual content.
      const resource = await session.send('Network.loadNetworkResource', {
        url: request.request.url(),
        frameId: this._serviceWorker ? undefined : request.request.frame()._id,
        options: {
          disableCache: false,
          includeCredentials: true
        }
      });
      const chunks = [];
      while (resource.resource.stream) {
        const chunk = await session.send('IO.read', {
          handle: resource.resource.stream
        });
        chunks.push(Buffer.from(chunk.data, chunk.base64Encoded ? 'base64' : 'utf-8'));
        if (chunk.eof) {
          await session.send('IO.close', {
            handle: resource.resource.stream
          });
          break;
        }
      }
      return Buffer.concat(chunks);
    };
    const timingPayload = responsePayload.timing;
    let timing;
    if (timingPayload && !this._responseExtraInfoTracker.servedFromCache(request._requestId)) {
      timing = {
        startTime: (timingPayload.requestTime - request._timestamp + request._wallTime) * 1000,
        domainLookupStart: timingPayload.dnsStart,
        domainLookupEnd: timingPayload.dnsEnd,
        connectStart: timingPayload.connectStart,
        secureConnectionStart: timingPayload.sslStart,
        connectEnd: timingPayload.connectEnd,
        requestStart: timingPayload.sendStart,
        responseStart: timingPayload.receiveHeadersEnd
      };
    } else {
      timing = {
        startTime: request._wallTime * 1000,
        domainLookupStart: -1,
        domainLookupEnd: -1,
        connectStart: -1,
        secureConnectionStart: -1,
        connectEnd: -1,
        requestStart: -1,
        responseStart: -1
      };
    }
    const response = new network.Response(request.request, responsePayload.status, responsePayload.statusText, (0, _utils.headersObjectToArray)(responsePayload.headers), timing, getResponseBody, !!responsePayload.fromServiceWorker, responsePayload.protocol);
    if (responsePayload?.remoteIPAddress && typeof responsePayload?.remotePort === 'number') {
      response._serverAddrFinished({
        ipAddress: responsePayload.remoteIPAddress,
        port: responsePayload.remotePort
      });
    } else {
      response._serverAddrFinished();
    }
    response._securityDetailsFinished({
      protocol: responsePayload?.securityDetails?.protocol,
      subjectName: responsePayload?.securityDetails?.subjectName,
      issuer: responsePayload?.securityDetails?.issuer,
      validFrom: responsePayload?.securityDetails?.validFrom,
      validTo: responsePayload?.securityDetails?.validTo
    });
    this._responseExtraInfoTracker.processResponse(request._requestId, response, hasExtraInfo);
    return response;
  }
  _deleteRequest(request) {
    this._requestIdToRequest.delete(request._requestId);
    if (request._interceptionId) this._attemptedAuthentications.delete(request._interceptionId);
  }
  _handleRequestRedirect(request, responsePayload, timestamp, hasExtraInfo) {
    const response = this._createResponse(request, responsePayload, hasExtraInfo);
    response.setTransferSize(null);
    response.setEncodedBodySize(null);
    response._requestFinished((timestamp - request._timestamp) * 1000);
    this._deleteRequest(request);
    (this._page?._frameManager || this._serviceWorker).requestReceivedResponse(response);
    (this._page?._frameManager || this._serviceWorker).reportRequestFinished(request.request, response);
  }
  _onResponseReceivedExtraInfo(event) {
    this._responseExtraInfoTracker.responseReceivedExtraInfo(event);
  }
  _onResponseReceived(sessionInfo, event) {
    let request = this._requestIdToRequest.get(event.requestId);
    // For frame-level Requests that are handled by a Service Worker's fetch handler, we'll never get a requestPaused event, so we need to
    // manually create the request. In an ideal world, crNetworkManager would be able to know this on Network.requestWillBeSent, but there
    // is not enough metadata there.
    if (!request && event.response.fromServiceWorker) {
      const requestWillBeSentEvent = this._requestIdToRequestWillBeSentEvent.get(event.requestId);
      if (requestWillBeSentEvent) {
        this._requestIdToRequestWillBeSentEvent.delete(event.requestId);
        this._onRequest(sessionInfo, requestWillBeSentEvent.event, undefined, undefined);
        request = this._requestIdToRequest.get(event.requestId);
      }
    }
    // FileUpload sends a response without a matching request.
    if (!request) return;
    const response = this._createResponse(request, event.response, event.hasExtraInfo);
    (this._page?._frameManager || this._serviceWorker).requestReceivedResponse(response);
  }
  _onLoadingFinished(sessionInfo, event) {
    this._responseExtraInfoTracker.loadingFinished(event);
    const request = this._requestIdToRequest.get(event.requestId);
    // For certain requestIds we never receive requestWillBeSent event.
    // @see https://crbug.com/750469
    if (!request) return;
    this._maybeUpdateOOPIFMainRequest(sessionInfo, request);

    // Under certain conditions we never get the Network.responseReceived
    // event from protocol. @see https://crbug.com/883475
    const response = request.request._existingResponse();
    if (response) {
      response.setTransferSize(event.encodedDataLength);
      response.responseHeadersSize().then(size => response.setEncodedBodySize(event.encodedDataLength - size));
      response._requestFinished(_helper.helper.secondsToRoundishMillis(event.timestamp - request._timestamp));
    }
    this._deleteRequest(request);
    (this._page?._frameManager || this._serviceWorker).reportRequestFinished(request.request, response);
  }
  _onLoadingFailed(sessionInfo, event) {
    this._responseExtraInfoTracker.loadingFailed(event);
    let request = this._requestIdToRequest.get(event.requestId);
    if (!request) {
      const requestWillBeSentEvent = this._requestIdToRequestWillBeSentEvent.get(event.requestId);
      if (requestWillBeSentEvent) {
        // This is a case where request has failed before we had a chance to intercept it.
        // We stop waiting for Fetch.requestPaused (it might never come), and dispatch request event
        // right away, followed by requestfailed event.
        this._requestIdToRequestWillBeSentEvent.delete(event.requestId);
        this._onRequest(sessionInfo, requestWillBeSentEvent.event, undefined, undefined);
        request = this._requestIdToRequest.get(event.requestId);
      }
    }

    // For certain requestIds we never receive requestWillBeSent event.
    // @see https://crbug.com/750469
    if (!request) return;
    this._maybeUpdateOOPIFMainRequest(sessionInfo, request);
    const response = request.request._existingResponse();
    if (response) {
      response.setTransferSize(null);
      response.setEncodedBodySize(null);
      response._requestFinished(_helper.helper.secondsToRoundishMillis(event.timestamp - request._timestamp));
    } else {
      // Loading failed before response has arrived - there will be no extra info events.
      request.request.setRawRequestHeaders(null);
    }
    this._deleteRequest(request);
    request.request._setFailureText(event.errorText || event.blockedReason || '');
    (this._page?._frameManager || this._serviceWorker).requestFailed(request.request, !!event.canceled);
  }
  _maybeUpdateOOPIFMainRequest(sessionInfo, request) {
    // OOPIF has a main request that starts in the parent session but finishes in the child session.
    // We check for the main request by matching loaderId and requestId, and if it now belongs to
    // a child session, migrate it there.
    if (request.session !== sessionInfo.session && !sessionInfo.isMain && request._documentId === request._requestId) request.session = sessionInfo.session;
  }
}
exports.CRNetworkManager = CRNetworkManager;
class InterceptableRequest {
  constructor(options) {
    this.request = void 0;
    this._requestId = void 0;
    this._interceptionId = void 0;
    this._documentId = void 0;
    this._timestamp = void 0;
    this._wallTime = void 0;
    this._route = void 0;
    // Only first request in the chain can be intercepted, so this will
    // store the first and only Route in the chain (if any).
    this._originalRequestRoute = void 0;
    this.session = void 0;
    const {
      session,
      context,
      frame,
      documentId,
      route,
      requestWillBeSentEvent,
      requestPausedEvent,
      redirectedFrom,
      serviceWorker,
      headersOverride
    } = options;
    this.session = session;
    this._timestamp = requestWillBeSentEvent.timestamp;
    this._wallTime = requestWillBeSentEvent.wallTime;
    this._requestId = requestWillBeSentEvent.requestId;
    this._interceptionId = requestPausedEvent && requestPausedEvent.requestId;
    this._documentId = documentId;
    this._route = route;
    this._originalRequestRoute = route !== null && route !== void 0 ? route : redirectedFrom?._originalRequestRoute;
    const {
      headers,
      method,
      url,
      postDataEntries = null
    } = requestPausedEvent ? requestPausedEvent.request : requestWillBeSentEvent.request;
    const type = (requestWillBeSentEvent.type || '').toLowerCase();
    let postDataBuffer = null;
    const entries = postDataEntries?.filter(entry => entry.bytes);
    if (entries && entries.length) postDataBuffer = Buffer.concat(entries.map(entry => Buffer.from(entry.bytes, 'base64')));
    this.request = new network.Request(context, frame, serviceWorker, redirectedFrom?.request || null, documentId, url, type, method, postDataBuffer, headersOverride || (0, _utils.headersObjectToArray)(headers));
  }
}
class RouteImpl {
  constructor(session, interceptionId, page, networkId, sessionManager) {
    this._session = void 0;
    this._interceptionId = void 0;
    this._alreadyContinuedParams = void 0;
    this._fulfilled = false;
    this._sessionManager = void 0;
    this._networkId = void 0;
    this._page = void 0;
    this._session = session;
    this._interceptionId = interceptionId;
    this._page = page;
    this._networkId = networkId;
    this._sessionManager = sessionManager;
    _eventsHelper.eventsHelper.addEventListener(this._session, 'Fetch.requestPaused', async e => await this._networkRequestIntercepted(e));
  }
  async continue(overrides) {
    this._alreadyContinuedParams = {
      requestId: this._interceptionId,
      url: overrides.url,
      headers: overrides.headers,
      method: overrides.method,
      postData: overrides.postData ? overrides.postData.toString('base64') : undefined
    };
    if (overrides.url && (overrides.url === 'http://patchright-init-script-inject.internal/' || overrides.url === 'https://patchright-init-script-inject.internal/')) {
      await catchDisallowedErrors(async () => {
        this._sessionManager._alreadyTrackedNetworkIds.add(this._networkId);
        this._session.send('Fetch.continueRequest', {
          requestId: this._interceptionId,
          interceptResponse: true
        });
      });
    } else {
      await catchDisallowedErrors(async () => {
        await this._session.send('Fetch.continueRequest', this._alreadyContinuedParams);
      });
    }
  }
  async fulfill(response) {
    const isTextHtml = response.resourceType === 'Document' || response.headers.some(header => header.name === 'content-type' && header.value.includes('text/html'));
    var allInjections = [...this._page._delegate._mainFrameSession._evaluateOnNewDocumentScripts];
    for (const binding of this._page._delegate._browserContext._pageBindings.values()) {
      if (!allInjections.includes(binding)) allInjections.push(binding);
    }
    if (isTextHtml && allInjections.length) {
      // I Chatted so hard for this Code
      let scriptNonce = _crypto.default.randomBytes(22).toString('hex');
      for (let i = 0; i < response.headers.length; i++) {
        if (response.headers[i].name === 'content-security-policy' || response.headers[i].name === 'content-security-policy-report-only') {
          // Search for an existing script-src nonce that we can hijack
          let cspValue = response.headers[i].value;
          const nonceRegex = /script-src[^;]*'nonce-([\w-]+)'/;
          const nonceMatch = cspValue.match(nonceRegex);
          if (nonceMatch) {
            scriptNonce = nonceMatch[1];
          } else {
            // Add the new nonce value to the script-src directive
            const scriptSrcRegex = /(script-src[^;]*)(;|$)/;
            const newCspValue = cspValue.replace(scriptSrcRegex, `$1 'nonce-${scriptNonce}'$2`);
            response.headers[i].value = newCspValue;
          }
          break;
        }
      }
      let injectionHTML = "";
      allInjections.forEach(script => {
        let scriptId = _crypto.default.randomBytes(22).toString('hex');
        injectionHTML += `<script class="${this._page._delegate.initScriptTag}" nonce="${scriptNonce}" type="text/javascript">document.getElementById("${scriptId}")?.remove();${script.source}</script>`;
      });
      if (response.isBase64) {
        response.isBase64 = false;
        response.body = injectionHTML + Buffer.from(response.body, 'base64').toString('utf-8');
      } else {
        response.body = injectionHTML + response.body;
      }
    }
    this._fulfilled = true;
    const body = response.isBase64 ? response.body : Buffer.from(response.body).toString('base64');
    const responseHeaders = splitSetCookieHeader(response.headers);
    await catchDisallowedErrors(async () => {
      await this._session.send('Fetch.fulfillRequest', {
        requestId: response.interceptionId ? response.interceptionId : this._interceptionId,
        responseCode: response.status,
        responsePhrase: network.statusText(response.status),
        responseHeaders,
        body
      });
    });
  }
  async abort(errorCode = 'failed') {
    const errorReason = errorReasons[errorCode];
    (0, _utils.assert)(errorReason, 'Unknown error code: ' + errorCode);
    await catchDisallowedErrors(async () => {
      await this._session.send('Fetch.failRequest', {
        requestId: this._interceptionId,
        errorReason
      });
    });
  }
  async _networkRequestIntercepted(event) {
    if (event.resourceType !== 'Document') {
      /*await catchDisallowedErrors(async () => {
        await this._session.send('Fetch.continueRequest', { requestId: event.requestId });
      });*/
      return;
    }
    if (this._networkId != event.networkId || !this._sessionManager._alreadyTrackedNetworkIds.has(event.networkId)) return;
    try {
      if (event.responseStatusCode >= 301 && event.responseStatusCode <= 308 || event.redirectedRequestId && !event.responseStatusCode) {
        await this._session.send('Fetch.continueRequest', {
          requestId: event.requestId,
          interceptResponse: true
        });
      } else {
        const responseBody = await this._session.send('Fetch.getResponseBody', {
          requestId: event.requestId
        });
        await this.fulfill({
          headers: event.responseHeaders,
          isBase64: true,
          body: responseBody.body,
          status: event.responseStatusCode,
          interceptionId: event.requestId,
          resourceType: event.resourceType
        });
      }
    } catch (error) {
      await this._session._sendMayFail('Fetch.continueRequest', {
        requestId: event.requestId
      });
    }
  }
}

// In certain cases, protocol will return error if the request was already canceled
// or the page was closed. We should tolerate these errors but propagate other.
async function catchDisallowedErrors(callback) {
  try {
    return await callback();
  } catch (e) {
    if ((0, _protocolError.isProtocolError)(e) && e.message.includes('Invalid http status code or phrase')) throw e;
  }
}
function splitSetCookieHeader(headers) {
  const index = headers.findIndex(({
    name
  }) => name.toLowerCase() === 'set-cookie');
  if (index === -1) return headers;
  const header = headers[index];
  const values = header.value.split('\n');
  if (values.length === 1) return headers;
  const result = headers.slice();
  result.splice(index, 1, ...values.map(value => ({
    name: header.name,
    value
  })));
  return result;
}
const errorReasons = {
  'aborted': 'Aborted',
  'accessdenied': 'AccessDenied',
  'addressunreachable': 'AddressUnreachable',
  'blockedbyclient': 'BlockedByClient',
  'blockedbyresponse': 'BlockedByResponse',
  'connectionaborted': 'ConnectionAborted',
  'connectionclosed': 'ConnectionClosed',
  'connectionfailed': 'ConnectionFailed',
  'connectionrefused': 'ConnectionRefused',
  'connectionreset': 'ConnectionReset',
  'internetdisconnected': 'InternetDisconnected',
  'namenotresolved': 'NameNotResolved',
  'timedout': 'TimedOut',
  'failed': 'Failed'
};
// This class aligns responses with response headers from extra info:
//   - Network.requestWillBeSent, Network.responseReceived, Network.loadingFinished/loadingFailed are
//     dispatched using one channel.
//   - Network.requestWillBeSentExtraInfo and Network.responseReceivedExtraInfo are dispatched on
//     another channel. Those channels are not associated, so events come in random order.
//
// This class will associate responses with the new headers. These extra info headers will become
// available to client reliably upon requestfinished event only. It consumes CDP
// signals on one end and processResponse(network.Response) signals on the other hands. It then makes
// sure that responses have all the extra headers in place by the time request finishes.
//
// The shape of the instrumentation API is deliberately following the CDP, so that it
// is clear what is called when and what this means to the tracker without extra
// documentation.
class ResponseExtraInfoTracker {
  constructor() {
    this._requests = new Map();
  }
  requestWillBeSentExtraInfo(event) {
    const info = this._getOrCreateEntry(event.requestId);
    info.requestWillBeSentExtraInfo.push(event);
    this._patchHeaders(info, info.requestWillBeSentExtraInfo.length - 1);
    this._checkFinished(info);
  }
  requestServedFromCache(event) {
    const info = this._getOrCreateEntry(event.requestId);
    info.servedFromCache = true;
  }
  servedFromCache(requestId) {
    const info = this._requests.get(requestId);
    return !!info?.servedFromCache;
  }
  responseReceivedExtraInfo(event) {
    const info = this._getOrCreateEntry(event.requestId);
    info.responseReceivedExtraInfo.push(event);
    this._patchHeaders(info, info.responseReceivedExtraInfo.length - 1);
    this._checkFinished(info);
  }
  processResponse(requestId, response, hasExtraInfo) {
    let info = this._requests.get(requestId);
    // Cached responses have erroneous "hasExtraInfo" flag.
    // https://bugs.chromium.org/p/chromium/issues/detail?id=1340398
    if (!hasExtraInfo || info?.servedFromCache) {
      // Use "provisional" headers as "raw" ones.
      response.request().setRawRequestHeaders(null);
      response.setResponseHeadersSize(null);
      response.setRawResponseHeaders(null);
      return;
    }
    info = this._getOrCreateEntry(requestId);
    info.responses.push(response);
    this._patchHeaders(info, info.responses.length - 1);
  }
  loadingFinished(event) {
    const info = this._requests.get(event.requestId);
    if (!info) return;
    info.loadingFinished = event;
    this._checkFinished(info);
  }
  loadingFailed(event) {
    const info = this._requests.get(event.requestId);
    if (!info) return;
    info.loadingFailed = event;
    this._checkFinished(info);
  }
  _getOrCreateEntry(requestId) {
    let info = this._requests.get(requestId);
    if (!info) {
      info = {
        requestId: requestId,
        requestWillBeSentExtraInfo: [],
        responseReceivedExtraInfo: [],
        responses: []
      };
      this._requests.set(requestId, info);
    }
    return info;
  }
  _patchHeaders(info, index) {
    const response = info.responses[index];
    const requestExtraInfo = info.requestWillBeSentExtraInfo[index];
    if (response && requestExtraInfo) {
      response.request().setRawRequestHeaders((0, _utils.headersObjectToArray)(requestExtraInfo.headers, '\n'));
      info.requestWillBeSentExtraInfo[index] = undefined;
    }
    const responseExtraInfo = info.responseReceivedExtraInfo[index];
    if (response && responseExtraInfo) {
      response.setResponseHeadersSize(responseExtraInfo.headersText?.length || 0);
      response.setRawResponseHeaders((0, _utils.headersObjectToArray)(responseExtraInfo.headers, '\n'));
      info.responseReceivedExtraInfo[index] = undefined;
    }
  }
  _checkFinished(info) {
    if (!info.loadingFinished && !info.loadingFailed) return;
    if (info.responses.length <= info.responseReceivedExtraInfo.length) {
      // We have extra info for each response.
      this._stopTracking(info.requestId);
      return;
    }

    // We are not done yet.
  }
  _stopTracking(requestId) {
    this._requests.delete(requestId);
  }
}