"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.BidiDeserializer = void 0;
/**
 * @license
 * Copyright 2024 Google Inc.
 * Modifications copyright (c) Microsoft Corporation.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable object-curly-spacing */

/**
 * @internal
 */
class BidiDeserializer {
  static deserialize(result) {
    if (!result) return undefined;
    switch (result.type) {
      case 'array':
        return result.value?.map(value => {
          return BidiDeserializer.deserialize(value);
        });
      case 'set':
        return result.value?.reduce((acc, value) => {
          return acc.add(BidiDeserializer.deserialize(value));
        }, new Set());
      case 'object':
        return result.value?.reduce((acc, tuple) => {
          const {
            key,
            value
          } = BidiDeserializer._deserializeTuple(tuple);
          acc[key] = value;
          return acc;
        }, {});
      case 'map':
        return result.value?.reduce((acc, tuple) => {
          const {
            key,
            value
          } = BidiDeserializer._deserializeTuple(tuple);
          return acc.set(key, value);
        }, new Map());
      case 'promise':
        return {};
      case 'regexp':
        return new RegExp(result.value.pattern, result.value.flags);
      case 'date':
        return new Date(result.value);
      case 'undefined':
        return undefined;
      case 'null':
        return null;
      case 'number':
        return BidiDeserializer._deserializeNumber(result.value);
      case 'bigint':
        return BigInt(result.value);
      case 'boolean':
        return Boolean(result.value);
      case 'string':
        return result.value;
    }
    throw new Error(`Deserialization of type ${result.type} not supported.`);
  }
  static _deserializeNumber(value) {
    switch (value) {
      case '-0':
        return -0;
      case 'NaN':
        return NaN;
      case 'Infinity':
        return Infinity;
      case '-Infinity':
        return -Infinity;
      default:
        return value;
    }
  }
  static _deserializeTuple([serializedKey, serializedValue]) {
    const key = typeof serializedKey === 'string' ? serializedKey : BidiDeserializer.deserialize(serializedKey);
    const value = BidiDeserializer.deserialize(serializedValue);
    return {
      key,
      value
    };
  }
}
exports.BidiDeserializer = BidiDeserializer;