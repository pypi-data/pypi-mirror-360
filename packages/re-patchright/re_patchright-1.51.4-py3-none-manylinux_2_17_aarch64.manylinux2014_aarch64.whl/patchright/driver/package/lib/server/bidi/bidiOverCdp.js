"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.connectBidiOverCdp = connectBidiOverCdp;
var bidiMapper = _interopRequireWildcard(require("chromium-bidi/lib/cjs/bidiMapper/BidiMapper"));
var bidiCdpConnection = _interopRequireWildcard(require("chromium-bidi/lib/cjs/cdp/CdpConnection"));
var _debugLogger = require("../utils/debugLogger");
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function (e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { default: e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && {}.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n.default = e, t && t.set(e, n), n; }
/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the 'License');
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an 'AS IS' BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const bidiServerLogger = (prefix, ...args) => {
  _debugLogger.debugLogger.log(prefix, args);
};
async function connectBidiOverCdp(cdp) {
  let server = undefined;
  const bidiTransport = new BidiTransportImpl();
  const bidiConnection = new BidiConnection(bidiTransport, () => server?.close());
  const cdpTransportImpl = new CdpTransportImpl(cdp);
  const cdpConnection = new bidiCdpConnection.MapperCdpConnection(cdpTransportImpl, bidiServerLogger);
  // Make sure onclose event is propagated.
  cdp.onclose = () => bidiConnection.onclose?.();
  server = await bidiMapper.BidiServer.createAndStart(bidiTransport, cdpConnection, await cdpConnection.createBrowserSession(), /* selfTargetId= */'', undefined, bidiServerLogger);
  return bidiConnection;
}
class BidiTransportImpl {
  constructor() {
    this._handler = void 0;
    this._bidiConnection = void 0;
  }
  setOnMessage(handler) {
    this._handler = handler;
  }
  sendMessage(message) {
    return this._bidiConnection.onmessage?.(message);
  }
  close() {
    this._bidiConnection.onclose?.();
  }
}
class BidiConnection {
  constructor(bidiTransport, closeCallback) {
    this._bidiTransport = void 0;
    this._closeCallback = void 0;
    this.onmessage = void 0;
    this.onclose = void 0;
    this._bidiTransport = bidiTransport;
    this._bidiTransport._bidiConnection = this;
    this._closeCallback = closeCallback;
  }
  send(s) {
    this._bidiTransport._handler?.(s);
  }
  close() {
    this._closeCallback();
  }
}
class CdpTransportImpl {
  constructor(connection) {
    this._connection = void 0;
    this._handler = void 0;
    this._bidiConnection = void 0;
    this._connection = connection;
    this._connection.onmessage = message => {
      this._handler?.(JSON.stringify(message));
    };
  }
  setOnMessage(handler) {
    this._handler = handler;
  }
  sendMessage(message) {
    return this._connection.send(JSON.parse(message));
  }
  close() {
    this._connection.close();
  }
}