import { computed as Ht, watch as yt, defineComponent as Vt, useTemplateRef as Yt, shallowRef as Kt, onMounted as Wt, useAttrs as Zt, createElementBlock as qt, openBlock as Jt, mergeProps as Qt, unref as kt } from "vue";
import * as mt from "echarts";
import { useVarGetter as te } from "instaui";
var vt = typeof global == "object" && global && global.Object === Object && global, ee = typeof self == "object" && self && self.Object === Object && self, I = vt || ee || Function("return this")(), _ = I.Symbol, _t = Object.prototype, ne = _t.hasOwnProperty, re = _t.toString, T = _ ? _.toStringTag : void 0;
function ie(t) {
  var e = ne.call(t, T), n = t[T];
  try {
    t[T] = void 0;
    var r = !0;
  } catch {
  }
  var i = re.call(t);
  return r && (e ? t[T] = n : delete t[T]), i;
}
var oe = Object.prototype, ae = oe.toString;
function se(t) {
  return ae.call(t);
}
var ce = "[object Null]", fe = "[object Undefined]", Q = _ ? _.toStringTag : void 0;
function C(t) {
  return t == null ? t === void 0 ? fe : ce : Q && Q in Object(t) ? ie(t) : se(t);
}
function A(t) {
  return t != null && typeof t == "object";
}
var ue = "[object Symbol]";
function N(t) {
  return typeof t == "symbol" || A(t) && C(t) == ue;
}
function de(t, e) {
  for (var n = -1, r = t == null ? 0 : t.length, i = Array(r); ++n < r; )
    i[n] = e(t[n], n, t);
  return i;
}
var b = Array.isArray, k = _ ? _.prototype : void 0, tt = k ? k.toString : void 0;
function bt(t) {
  if (typeof t == "string")
    return t;
  if (b(t))
    return de(t, bt) + "";
  if (N(t))
    return tt ? tt.call(t) : "";
  var e = t + "";
  return e == "0" && 1 / t == -1 / 0 ? "-0" : e;
}
function x(t) {
  var e = typeof t;
  return t != null && (e == "object" || e == "function");
}
function It(t) {
  return t;
}
var le = "[object AsyncFunction]", pe = "[object Function]", ge = "[object GeneratorFunction]", he = "[object Proxy]";
function X(t) {
  if (!x(t))
    return !1;
  var e = C(t);
  return e == pe || e == ge || e == le || e == he;
}
var F = I["__core-js_shared__"], et = function() {
  var t = /[^.]+$/.exec(F && F.keys && F.keys.IE_PROTO || "");
  return t ? "Symbol(src)_1." + t : "";
}();
function xe(t) {
  return !!et && et in t;
}
var ye = Function.prototype, me = ye.toString;
function ve(t) {
  if (t != null) {
    try {
      return me.call(t);
    } catch {
    }
    try {
      return t + "";
    } catch {
    }
  }
  return "";
}
var _e = /[\\^$.*+?()[\]{}|]/g, be = /^\[object .+?Constructor\]$/, Ie = Function.prototype, Ae = Object.prototype, Oe = Ie.toString, we = Ae.hasOwnProperty, Se = RegExp(
  "^" + Oe.call(we).replace(_e, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
);
function Te(t) {
  if (!x(t) || xe(t))
    return !1;
  var e = X(t) ? Se : be;
  return e.test(ve(t));
}
function Me(t, e) {
  return t?.[e];
}
function B(t, e) {
  var n = Me(t, e);
  return Te(n) ? n : void 0;
}
var nt = Object.create, $e = /* @__PURE__ */ function() {
  function t() {
  }
  return function(e) {
    if (!x(e))
      return {};
    if (nt)
      return nt(e);
    t.prototype = e;
    var n = new t();
    return t.prototype = void 0, n;
  };
}();
function Ce(t, e, n) {
  switch (n.length) {
    case 0:
      return t.call(e);
    case 1:
      return t.call(e, n[0]);
    case 2:
      return t.call(e, n[0], n[1]);
    case 3:
      return t.call(e, n[0], n[1], n[2]);
  }
  return t.apply(e, n);
}
function je(t, e) {
  var n = -1, r = t.length;
  for (e || (e = Array(r)); ++n < r; )
    e[n] = t[n];
  return e;
}
var Ee = 800, Pe = 16, De = Date.now;
function Fe(t) {
  var e = 0, n = 0;
  return function() {
    var r = De(), i = Pe - (r - n);
    if (n = r, i > 0) {
      if (++e >= Ee)
        return arguments[0];
    } else
      e = 0;
    return t.apply(void 0, arguments);
  };
}
function ze(t) {
  return function() {
    return t;
  };
}
var j = function() {
  try {
    var t = B(Object, "defineProperty");
    return t({}, "", {}), t;
  } catch {
  }
}(), Re = j ? function(t, e) {
  return j(t, "toString", {
    configurable: !0,
    enumerable: !1,
    value: ze(e),
    writable: !0
  });
} : It, Ge = Fe(Re), Ue = 9007199254740991, Ne = /^(?:0|[1-9]\d*)$/;
function L(t, e) {
  var n = typeof t;
  return e = e ?? Ue, !!e && (n == "number" || n != "symbol" && Ne.test(t)) && t > -1 && t % 1 == 0 && t < e;
}
function H(t, e, n) {
  e == "__proto__" && j ? j(t, e, {
    configurable: !0,
    enumerable: !0,
    value: n,
    writable: !0
  }) : t[e] = n;
}
function E(t, e) {
  return t === e || t !== t && e !== e;
}
var Xe = Object.prototype, Be = Xe.hasOwnProperty;
function At(t, e, n) {
  var r = t[e];
  (!(Be.call(t, e) && E(r, n)) || n === void 0 && !(e in t)) && H(t, e, n);
}
function Le(t, e, n, r) {
  var i = !n;
  n || (n = {});
  for (var a = -1, o = e.length; ++a < o; ) {
    var s = e[a], c = void 0;
    c === void 0 && (c = t[s]), i ? H(n, s, c) : At(n, s, c);
  }
  return n;
}
var rt = Math.max;
function He(t, e, n) {
  return e = rt(e === void 0 ? t.length - 1 : e, 0), function() {
    for (var r = arguments, i = -1, a = rt(r.length - e, 0), o = Array(a); ++i < a; )
      o[i] = r[e + i];
    i = -1;
    for (var s = Array(e + 1); ++i < e; )
      s[i] = r[i];
    return s[e] = n(o), Ce(t, this, s);
  };
}
function Ve(t, e) {
  return Ge(He(t, e, It), t + "");
}
var Ye = 9007199254740991;
function Ot(t) {
  return typeof t == "number" && t > -1 && t % 1 == 0 && t <= Ye;
}
function V(t) {
  return t != null && Ot(t.length) && !X(t);
}
function Ke(t, e, n) {
  if (!x(n))
    return !1;
  var r = typeof e;
  return (r == "number" ? V(n) && L(e, n.length) : r == "string" && e in n) ? E(n[e], t) : !1;
}
function wt(t) {
  return Ve(function(e, n) {
    var r = -1, i = n.length, a = i > 1 ? n[i - 1] : void 0, o = i > 2 ? n[2] : void 0;
    for (a = t.length > 3 && typeof a == "function" ? (i--, a) : void 0, o && Ke(n[0], n[1], o) && (a = i < 3 ? void 0 : a, i = 1), e = Object(e); ++r < i; ) {
      var s = n[r];
      s && t(e, s, r, a);
    }
    return e;
  });
}
var We = Object.prototype;
function St(t) {
  var e = t && t.constructor, n = typeof e == "function" && e.prototype || We;
  return t === n;
}
function Ze(t, e) {
  for (var n = -1, r = Array(t); ++n < t; )
    r[n] = e(n);
  return r;
}
var qe = "[object Arguments]";
function it(t) {
  return A(t) && C(t) == qe;
}
var Tt = Object.prototype, Je = Tt.hasOwnProperty, Qe = Tt.propertyIsEnumerable, R = it(/* @__PURE__ */ function() {
  return arguments;
}()) ? it : function(t) {
  return A(t) && Je.call(t, "callee") && !Qe.call(t, "callee");
};
function ke() {
  return !1;
}
var Mt = typeof exports == "object" && exports && !exports.nodeType && exports, ot = Mt && typeof module == "object" && module && !module.nodeType && module, tn = ot && ot.exports === Mt, at = tn ? I.Buffer : void 0, en = at ? at.isBuffer : void 0, $t = en || ke, nn = "[object Arguments]", rn = "[object Array]", on = "[object Boolean]", an = "[object Date]", sn = "[object Error]", cn = "[object Function]", fn = "[object Map]", un = "[object Number]", dn = "[object Object]", ln = "[object RegExp]", pn = "[object Set]", gn = "[object String]", hn = "[object WeakMap]", xn = "[object ArrayBuffer]", yn = "[object DataView]", mn = "[object Float32Array]", vn = "[object Float64Array]", _n = "[object Int8Array]", bn = "[object Int16Array]", In = "[object Int32Array]", An = "[object Uint8Array]", On = "[object Uint8ClampedArray]", wn = "[object Uint16Array]", Sn = "[object Uint32Array]", l = {};
l[mn] = l[vn] = l[_n] = l[bn] = l[In] = l[An] = l[On] = l[wn] = l[Sn] = !0;
l[nn] = l[rn] = l[xn] = l[on] = l[yn] = l[an] = l[sn] = l[cn] = l[fn] = l[un] = l[dn] = l[ln] = l[pn] = l[gn] = l[hn] = !1;
function Tn(t) {
  return A(t) && Ot(t.length) && !!l[C(t)];
}
function Mn(t) {
  return function(e) {
    return t(e);
  };
}
var Ct = typeof exports == "object" && exports && !exports.nodeType && exports, M = Ct && typeof module == "object" && module && !module.nodeType && module, $n = M && M.exports === Ct, z = $n && vt.process, st = function() {
  try {
    var t = M && M.require && M.require("util").types;
    return t || z && z.binding && z.binding("util");
  } catch {
  }
}(), ct = st && st.isTypedArray, jt = ct ? Mn(ct) : Tn;
function Cn(t, e) {
  var n = b(t), r = !n && R(t), i = !n && !r && $t(t), a = !n && !r && !i && jt(t), o = n || r || i || a, s = o ? Ze(t.length, String) : [], c = s.length;
  for (var f in t)
    o && // Safari 9 has enumerable `arguments.length` in strict mode.
    (f == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
    i && (f == "offset" || f == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
    a && (f == "buffer" || f == "byteLength" || f == "byteOffset") || // Skip index properties.
    L(f, c)) || s.push(f);
  return s;
}
function jn(t, e) {
  return function(n) {
    return t(e(n));
  };
}
function En(t) {
  var e = [];
  if (t != null)
    for (var n in Object(t))
      e.push(n);
  return e;
}
var Pn = Object.prototype, Dn = Pn.hasOwnProperty;
function Fn(t) {
  if (!x(t))
    return En(t);
  var e = St(t), n = [];
  for (var r in t)
    r == "constructor" && (e || !Dn.call(t, r)) || n.push(r);
  return n;
}
function Et(t) {
  return V(t) ? Cn(t) : Fn(t);
}
var zn = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, Rn = /^\w*$/;
function Gn(t, e) {
  if (b(t))
    return !1;
  var n = typeof t;
  return n == "number" || n == "symbol" || n == "boolean" || t == null || N(t) ? !0 : Rn.test(t) || !zn.test(t) || e != null && t in Object(e);
}
var $ = B(Object, "create");
function Un() {
  this.__data__ = $ ? $(null) : {}, this.size = 0;
}
function Nn(t) {
  var e = this.has(t) && delete this.__data__[t];
  return this.size -= e ? 1 : 0, e;
}
var Xn = "__lodash_hash_undefined__", Bn = Object.prototype, Ln = Bn.hasOwnProperty;
function Hn(t) {
  var e = this.__data__;
  if ($) {
    var n = e[t];
    return n === Xn ? void 0 : n;
  }
  return Ln.call(e, t) ? e[t] : void 0;
}
var Vn = Object.prototype, Yn = Vn.hasOwnProperty;
function Kn(t) {
  var e = this.__data__;
  return $ ? e[t] !== void 0 : Yn.call(e, t);
}
var Wn = "__lodash_hash_undefined__";
function Zn(t, e) {
  var n = this.__data__;
  return this.size += this.has(t) ? 0 : 1, n[t] = $ && e === void 0 ? Wn : e, this;
}
function v(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
v.prototype.clear = Un;
v.prototype.delete = Nn;
v.prototype.get = Hn;
v.prototype.has = Kn;
v.prototype.set = Zn;
function qn() {
  this.__data__ = [], this.size = 0;
}
function P(t, e) {
  for (var n = t.length; n--; )
    if (E(t[n][0], e))
      return n;
  return -1;
}
var Jn = Array.prototype, Qn = Jn.splice;
function kn(t) {
  var e = this.__data__, n = P(e, t);
  if (n < 0)
    return !1;
  var r = e.length - 1;
  return n == r ? e.pop() : Qn.call(e, n, 1), --this.size, !0;
}
function tr(t) {
  var e = this.__data__, n = P(e, t);
  return n < 0 ? void 0 : e[n][1];
}
function er(t) {
  return P(this.__data__, t) > -1;
}
function nr(t, e) {
  var n = this.__data__, r = P(n, t);
  return r < 0 ? (++this.size, n.push([t, e])) : n[r][1] = e, this;
}
function y(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
y.prototype.clear = qn;
y.prototype.delete = kn;
y.prototype.get = tr;
y.prototype.has = er;
y.prototype.set = nr;
var Pt = B(I, "Map");
function rr() {
  this.size = 0, this.__data__ = {
    hash: new v(),
    map: new (Pt || y)(),
    string: new v()
  };
}
function ir(t) {
  var e = typeof t;
  return e == "string" || e == "number" || e == "symbol" || e == "boolean" ? t !== "__proto__" : t === null;
}
function D(t, e) {
  var n = t.__data__;
  return ir(e) ? n[typeof e == "string" ? "string" : "hash"] : n.map;
}
function or(t) {
  var e = D(this, t).delete(t);
  return this.size -= e ? 1 : 0, e;
}
function ar(t) {
  return D(this, t).get(t);
}
function sr(t) {
  return D(this, t).has(t);
}
function cr(t, e) {
  var n = D(this, t), r = n.size;
  return n.set(t, e), this.size += n.size == r ? 0 : 1, this;
}
function m(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
m.prototype.clear = rr;
m.prototype.delete = or;
m.prototype.get = ar;
m.prototype.has = sr;
m.prototype.set = cr;
var fr = "Expected a function";
function Y(t, e) {
  if (typeof t != "function" || e != null && typeof e != "function")
    throw new TypeError(fr);
  var n = function() {
    var r = arguments, i = e ? e.apply(this, r) : r[0], a = n.cache;
    if (a.has(i))
      return a.get(i);
    var o = t.apply(this, r);
    return n.cache = a.set(i, o) || a, o;
  };
  return n.cache = new (Y.Cache || m)(), n;
}
Y.Cache = m;
var ur = 500;
function dr(t) {
  var e = Y(t, function(r) {
    return n.size === ur && n.clear(), r;
  }), n = e.cache;
  return e;
}
var lr = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, pr = /\\(\\)?/g, gr = dr(function(t) {
  var e = [];
  return t.charCodeAt(0) === 46 && e.push(""), t.replace(lr, function(n, r, i, a) {
    e.push(i ? a.replace(pr, "$1") : r || n);
  }), e;
});
function hr(t) {
  return t == null ? "" : bt(t);
}
function xr(t, e) {
  return b(t) ? t : Gn(t, e) ? [t] : gr(hr(t));
}
function yr(t) {
  if (typeof t == "string" || N(t))
    return t;
  var e = t + "";
  return e == "0" && 1 / t == -1 / 0 ? "-0" : e;
}
var Dt = jn(Object.getPrototypeOf, Object), mr = "[object Object]", vr = Function.prototype, _r = Object.prototype, Ft = vr.toString, br = _r.hasOwnProperty, Ir = Ft.call(Object);
function Ar(t) {
  if (!A(t) || C(t) != mr)
    return !1;
  var e = Dt(t);
  if (e === null)
    return !0;
  var n = br.call(e, "constructor") && e.constructor;
  return typeof n == "function" && n instanceof n && Ft.call(n) == Ir;
}
function Or() {
  this.__data__ = new y(), this.size = 0;
}
function wr(t) {
  var e = this.__data__, n = e.delete(t);
  return this.size = e.size, n;
}
function Sr(t) {
  return this.__data__.get(t);
}
function Tr(t) {
  return this.__data__.has(t);
}
var Mr = 200;
function $r(t, e) {
  var n = this.__data__;
  if (n instanceof y) {
    var r = n.__data__;
    if (!Pt || r.length < Mr - 1)
      return r.push([t, e]), this.size = ++n.size, this;
    n = this.__data__ = new m(r);
  }
  return n.set(t, e), this.size = n.size, this;
}
function O(t) {
  var e = this.__data__ = new y(t);
  this.size = e.size;
}
O.prototype.clear = Or;
O.prototype.delete = wr;
O.prototype.get = Sr;
O.prototype.has = Tr;
O.prototype.set = $r;
var zt = typeof exports == "object" && exports && !exports.nodeType && exports, ft = zt && typeof module == "object" && module && !module.nodeType && module, Cr = ft && ft.exports === zt, ut = Cr ? I.Buffer : void 0;
ut && ut.allocUnsafe;
function jr(t, e) {
  return t.slice();
}
var dt = I.Uint8Array;
function Er(t) {
  var e = new t.constructor(t.byteLength);
  return new dt(e).set(new dt(t)), e;
}
function Pr(t, e) {
  var n = Er(t.buffer);
  return new t.constructor(n, t.byteOffset, t.length);
}
function Dr(t) {
  return typeof t.constructor == "function" && !St(t) ? $e(Dt(t)) : {};
}
function Fr(t) {
  return function(e, n, r) {
    for (var i = -1, a = Object(e), o = r(e), s = o.length; s--; ) {
      var c = o[++i];
      if (n(a[c], c, a) === !1)
        break;
    }
    return e;
  };
}
var zr = Fr();
function G(t, e, n) {
  (n !== void 0 && !E(t[e], n) || n === void 0 && !(e in t)) && H(t, e, n);
}
function Rr(t) {
  return A(t) && V(t);
}
function U(t, e) {
  if (!(e === "constructor" && typeof t[e] == "function") && e != "__proto__")
    return t[e];
}
function Gr(t) {
  return Le(t, Et(t));
}
function Ur(t, e, n, r, i, a, o) {
  var s = U(t, n), c = U(e, n), f = o.get(c);
  if (f) {
    G(t, n, f);
    return;
  }
  var u = a ? a(s, c, n + "", t, e, o) : void 0, d = u === void 0;
  if (d) {
    var p = b(c), g = !p && $t(c), h = !p && !g && jt(c);
    u = c, p || g || h ? b(s) ? u = s : Rr(s) ? u = je(s) : g ? (d = !1, u = jr(c)) : h ? (d = !1, u = Pr(c)) : u = [] : Ar(c) || R(c) ? (u = s, R(s) ? u = Gr(s) : (!x(s) || X(s)) && (u = Dr(c))) : d = !1;
  }
  d && (o.set(c, u), i(u, c, r, a, o), o.delete(c)), G(t, n, u);
}
function K(t, e, n, r, i) {
  t !== e && zr(e, function(a, o) {
    if (i || (i = new O()), x(a))
      Ur(t, e, o, n, K, r, i);
    else {
      var s = r ? r(U(t, o), a, o + "", t, e, i) : void 0;
      s === void 0 && (s = a), G(t, o, s);
    }
  }, Et);
}
var Nr = wt(function(t, e, n, r) {
  K(t, e, n, r);
}), Xr = wt(function(t, e, n) {
  K(t, e, n);
});
function Br(t, e, n, r) {
  if (!x(t))
    return t;
  e = xr(e, t);
  for (var i = -1, a = e.length, o = a - 1, s = t; s != null && ++i < a; ) {
    var c = yr(e[i]), f = n;
    if (c === "__proto__" || c === "constructor" || c === "prototype")
      return t;
    if (i != o) {
      var u = s[c];
      f = void 0, f === void 0 && (f = x(u) ? u : L(e[i + 1]) ? [] : {});
    }
    At(s, c, f), s = s[c];
  }
  return t;
}
function Lr(t, e, n) {
  return t == null ? t : Br(t, e, n);
}
function Hr(t) {
  const e = Vr(t);
  return {
    ...t,
    dataId: e
  };
}
function Vr(t) {
  if (t.dataId)
    return t.dataId;
  for (const e of t.markSpecs)
    if (e.dataId)
      return e.dataId;
  throw new Error("No dataId found in specCollector");
}
function Yr(t) {
  return new Kr(Wr(t), t);
}
class Kr {
  constructor(e, n) {
    this.facetInfo = e, this.specCollector = n, this._fieldTypeMap = Zr(n);
  }
  _fieldTypeMap;
  /**
   * get
   */
  getDatasetSpec(e) {
    return this.specCollector.dataMap[e];
  }
  /**
   * getFieldType
   */
  getFieldType(e, n) {
    const r = this._fieldTypeMap.get(e);
    if (!r)
      throw new Error(`Unknown dataId: ${e}`);
    const i = r[n];
    if (!i)
      throw new Error(`Unknown field: ${n}`);
    return i;
  }
}
function Wr(t) {
  const { markSpecs: e, dataId: n } = t;
  let r = null, i = null, a = n;
  for (const o of e) {
    if (o.fx && r && o.fx !== r)
      throw new Error("Facet x is not consistent");
    if (o.fy && i && o.fy !== i)
      throw new Error("Facet y is not consistent");
    o.fx && (r = o.fx), o.fy && (i = o.fy), o.dataId && (a = o.dataId);
  }
  return {
    fx: r,
    fy: i,
    dataId: a
  };
}
function Zr(t) {
  const e = /* @__PURE__ */ new Map(), n = t.dataId;
  function r(i, a) {
    if (!a)
      return null;
    const o = t.dataMap[i], s = o.fields.indexOf(a), c = o.rows[0][s];
    return typeof c == "number" ? "number" : typeof c == "string" ? "string" : "unknown";
  }
  for (const { x: i, y: a, dataId: o } of t.markSpecs) {
    const s = o || n;
    [i, a].forEach((c) => {
      if (!c)
        return;
      const f = r(s, c);
      f && (e.has(s) || e.set(s, {}), e.get(s)[c] = f);
    });
  }
  return e;
}
class qr {
  id2datasetIndex = /* @__PURE__ */ new Map();
  datasetOption = [];
  seriesIndex2datasetIndex = /* @__PURE__ */ new Map();
  constructor() {
  }
  /**
   * addSource
   */
  addSource(e) {
    const n = this.datasetOption.push(e) - 1;
    return this.id2datasetIndex.set(e.id, n), n;
  }
  /**
   * addFilterSource
   */
  addFilterSource(e) {
    const { dataId: n, filterConditions: r } = e;
    return r.length === 0 ? this.getDatasetIndex(n) : this.datasetOption.push({
      transform: {
        fromDatasetId: n,
        type: "filter",
        config: {
          and: r.map((i) => ({
            dimension: i.field,
            "=": i.value
          }))
        }
      }
    }) - 1;
  }
  /**
   * getDatasetIndex
   */
  getDatasetIndex(e) {
    return this.id2datasetIndex.get(e);
  }
  /**
   * getDataset
   */
  getDataset(e, n) {
    const r = this.datasetOption[this.getDatasetIndex(e)];
    if (!n)
      return r;
    const { field: i } = n, a = r.dimensions.indexOf(i);
    return r.source.map((o) => [o[a]]);
  }
  /**
   * withDatasetIndex
   */
  withDatasetIndex(e, n) {
    return {
      ...n,
      datasetIndex: this.seriesIndex2datasetIndex.get(e)
    };
  }
  /**
   * getDatasetOption
   */
  getDatasetOption() {
    return this.datasetOption;
  }
  /**
   * getDatasetWithFilter
   */
  getDatasetWithFilter(e, n) {
    const { filter: r } = e.setting, { dataId: i } = e.setting.markSpec, a = this.datasetOption[this.getDatasetIndex(i)];
    if (!r)
      return a;
    const { filterConditions: o } = r, s = a.source.filter((u) => o.every((d) => {
      const p = a.dimensions.indexOf(d.field);
      return u[p] === d.value;
    })), { field: c } = n || {};
    if (!c)
      return {
        dimensions: a.dimensions,
        source: s
      };
    const f = a.dimensions.indexOf(c);
    return s.map((u) => [u[f]]);
  }
}
function Jr(t) {
  const e = new qr(), { specCollector: n, seriesModels: r } = t;
  for (const i in n.dataMap) {
    const { fields: a, rows: o } = n.dataMap[i];
    e.addSource({ id: i, dimensions: a, source: o });
  }
  return r.forEach((i, a) => {
    const { filter: o, markSpec: s } = i.setting, c = o ? e.addFilterSource(o) : e.getDatasetIndex(s.dataId);
    e.seriesIndex2datasetIndex.set(a, c);
  }), e;
}
const Qr = {
  paddingLeft: 2,
  paddingRight: 2,
  paddingTop: 15,
  paddingBottom: 2,
  colGap: 5,
  rowGap: 10
};
function kr(t, e) {
  const { fx: n, fy: r, dataId: i } = e.facetInfo, a = t.dataMap[i];
  let o, s;
  if (n) {
    const u = a.fields.indexOf(n);
    o = Array.from(new Set(a.rows.map((d) => d[u])));
  }
  if (r) {
    const u = a.fields.indexOf(r);
    s = Array.from(new Set(a.rows.map((d) => d[u])));
  }
  const c = [];
  let f = 0;
  for (const { xValue: u, yValue: d, config: p, fRow: g, fCol: h } of ei({
    xValues: o,
    yValues: s
  }))
    c.push(
      new ti({
        config: p,
        fxValue: u,
        fyValue: d,
        fRow: g,
        fCol: h,
        gridIndex: f
      })
    ), f++;
  return c;
}
class ti {
  constructor(e) {
    this.setting = e;
  }
  /**
   * getGridOption
   */
  getGridOption() {
    return { ...this.setting.config, containLabel: !0 };
  }
}
function* ei(t) {
  const {
    paddingLeft: e,
    paddingRight: n,
    paddingTop: r,
    paddingBottom: i,
    colGap: a,
    rowGap: o
  } = Qr, s = t.xValues || [], c = t.yValues || [], f = s.length, u = c.length;
  if (f === 0 && u === 0) {
    yield { config: {} };
    return;
  }
  const d = f > 0 ? s : ["_"], p = u > 0 ? c : ["_"], g = d.length, h = p.length, Gt = 100 - e - n - a * (g - 1), Ut = 100 - r - i - o * (h - 1), W = Gt / g, Z = Ut / h;
  for (let w = 0; w < h; w++)
    for (let S = 0; S < g; S++) {
      const Nt = d[S], Xt = p[w], q = e + S * (W + a), J = r + w * (Z + o), Bt = 100 - q - W, Lt = 100 - J - Z;
      yield {
        xValue: f > 0 ? Nt : null,
        yValue: u > 0 ? Xt : null,
        fRow: w,
        fCol: S,
        config: {
          left: `${q.toFixed(2)}%`,
          top: `${J.toFixed(2)}%`,
          right: `${Bt.toFixed(2)}%`,
          bottom: `${Lt.toFixed(2)}%`
        }
      };
    }
}
function ni(t) {
  return ri[t.markSpec.type](t);
}
const ri = {
  barY: ii,
  barX: oi,
  line: ai,
  point: si
};
function Rt(t, e) {
  const { markSpec: n, globalModel: r } = t, { x: i, y: a, color: o, dataId: s, extends: c = {} } = n, f = "bar";
  if (o) {
    const u = r.getDatasetSpec(s), d = u.fields.indexOf(o);
    return [...new Set(u.rows.map((h) => h[d]))].map((h) => ({
      config: {
        ...c,
        type: f,
        name: h,
        encode: {
          x: i,
          y: a
        }
      },
      colorInfo: {
        field: o,
        value: h
      }
    }));
  }
  return [
    {
      config: {
        type: f,
        encode: {
          x: i,
          y: a
        }
      }
    }
  ];
}
function ii(t) {
  return Rt(t);
}
function oi(t) {
  return Rt(t);
}
function ai(t) {
  const { markSpec: e, globalModel: n } = t, { x: r, y: i, color: a, dataId: o } = e, s = "line";
  if (a) {
    const c = n.getDatasetSpec(o), f = c.fields.indexOf(a);
    return [...new Set(c.rows.map((p) => p[f]))].map((p) => ({
      config: {
        type: s,
        name: p,
        encode: {
          x: r,
          y: i
        }
      },
      colorInfo: {
        field: a,
        value: p
      }
    }));
  }
  return [
    {
      config: {
        type: s,
        encode: {
          x: r,
          y: i
        }
      }
    }
  ];
}
function si(t) {
  const { markSpec: e, globalModel: n } = t, { x: r, y: i, color: a, dataId: o, size: s } = e, c = n.getDatasetSpec(o), f = {};
  if (s) {
    const u = c.fields.indexOf(s);
    f.symbolSize = (d) => d[u];
  }
  if (a) {
    const u = c.fields.indexOf(a);
    return [...new Set(c.rows.map((g) => g[u]))].map((g) => ({
      config: {
        type: "scatter",
        name: g,
        encode: {
          x: r,
          y: i
        },
        ...f
      },
      colorInfo: {
        field: a,
        value: g
      }
    }));
  }
  return [
    {
      config: {
        type: "scatter",
        encode: {
          x: r,
          y: i
        },
        ...f
      }
    }
  ];
}
class ci {
  constructor(e, n) {
    this.gridModel = e, this.setting = n;
  }
  /**
   * getSeriesOption
   */
  getSeriesOption() {
    const { config: e } = this.setting;
    return {
      ...e
    };
  }
}
function fi(t) {
  const { specCollector: e, gridModels: n, globalModel: r } = t;
  return n.flatMap((i) => e.markSpecs.flatMap((a) => {
    const o = {
      ...a,
      dataId: a.dataId || e.dataId
    };
    return ni({
      markSpec: o,
      globalModel: r
    }).map((c) => {
      const f = ui({
        markSpec: o,
        gridModel: i,
        colorInfo: c.colorInfo
      });
      return new ci(i, {
        config: c.config,
        markSpec: o,
        filter: f
      });
    });
  }));
}
function ui(t) {
  const { markSpec: e, gridModel: n, colorInfo: r } = t, { fx: i = null, fy: a = null, dataId: o } = e, s = [];
  return i && s.push({ field: i, value: n.setting.fxValue }), a && s.push({ field: a, value: n.setting.fyValue }), r && s.push({ field: r.field, value: r.value }), {
    dataId: o,
    filterConditions: s
  };
}
function di(t, e) {
  if (t === e) {
    const f = t === 0 ? 1 : Math.abs(t) * 0.1 || 1;
    return {
      step: f,
      niceMin: t - f,
      niceMax: e + f
    };
  }
  const r = (e - t) / 5, i = Math.pow(10, Math.floor(Math.log10(r))), a = r / i;
  let o;
  a <= 1 ? o = 1 : a <= 2 ? o = 2 : a <= 5 ? o = 5 : o = 10, o *= i;
  let s = Math.floor(t / o) * o, c = Math.ceil(e / o) * o;
  return { step: o, niceMin: s, niceMax: c };
}
class li {
  gridUsedXAxis = /* @__PURE__ */ new Map();
  gridUsedYAxis = /* @__PURE__ */ new Map();
  xAxisOptions = [];
  yAxisOptions = [];
  seriesIndex2xAxisIndex = /* @__PURE__ */ new Map();
  constructor() {
  }
  /**
   * tryAddxAxis
   */
  tryAddX(e) {
    const { config: n, gridIndex: r, field: i } = e, a = {
      ...n,
      gridIndex: r
    }, o = this.gridUsedXAxis.get(r) || /* @__PURE__ */ new Map();
    if (o.has(i))
      return o.get(i);
    const s = this.xAxisOptions.push(a) - 1;
    return o.set(i, s), this.gridUsedXAxis.set(r, o), s;
  }
  /**
   * getAxisLevel
   */
  getAxisLevel(e, n) {
    if (e === "x") {
      const r = this.gridUsedXAxis.get(n);
      return r ? r.size : 0;
    }
    if (e === "y") {
      const r = this.gridUsedYAxis.get(n);
      return r ? r.size : 0;
    }
    return -1;
  }
  /**
   * tryAddyAxis
   */
  tryAddY(e) {
    const { config: n, gridIndex: r, field: i } = e, a = {
      ...n,
      gridIndex: r
    }, o = this.gridUsedYAxis.get(r) || /* @__PURE__ */ new Map();
    if (o.has(i))
      return o.get(i);
    const s = this.yAxisOptions.push(a) - 1;
    return o.set(i, s), this.gridUsedYAxis.set(r, o), s;
  }
  /**
   * markSeriesModelAxisInfo
   */
  markSeriesModelAxisInfo(e) {
    const { seriesModelIndex: n, xAxisIndex: r, yAxisIndex: i } = e;
    this.seriesIndex2xAxisIndex.set(n, {
      xAxisIndex: r,
      yAxisIndex: i
    });
  }
  withAxisIndex(e, n) {
    const r = this.seriesIndex2xAxisIndex.get(e);
    return {
      ...n,
      xAxisIndex: r.xAxisIndex,
      yAxisIndex: r.yAxisIndex
    };
  }
  getXAxisOption() {
    return this.xAxisOptions;
  }
  getYAxisOption() {
    return this.yAxisOptions;
  }
}
function pi(t) {
  const e = new li(), { seriesModels: n, globalModel: r } = t, i = gi(t);
  return n.forEach((a, o) => {
    const { markSpec: s } = a.setting, f = a.gridModel.setting.gridIndex, u = i.withAxisRange(
      lt[s.type](r, s).xAxis,
      {
        type: "x",
        axisLevel: e.getAxisLevel("x", f)
      }
    ), d = e.tryAddX({
      config: u,
      gridIndex: f,
      field: s.x
    }), p = i.withAxisRange(
      lt[s.type](r, s).yAxis,
      {
        type: "y",
        axisLevel: e.getAxisLevel("y", f)
      }
    ), g = e.tryAddY({
      config: p,
      gridIndex: f,
      field: s.y
    });
    e.markSeriesModelAxisInfo({
      seriesModelIndex: o,
      xAxisIndex: d,
      yAxisIndex: g
    });
  }), e;
}
const lt = {
  barY: () => ({
    xAxis: { type: "category" },
    yAxis: { type: "value" }
  }),
  barX: () => ({
    xAxis: { type: "value" },
    yAxis: { type: "category" }
  }),
  line: pt,
  point: pt
};
function gi(t) {
  const { seriesModels: e } = t, n = /* @__PURE__ */ new Map(), r = /* @__PURE__ */ new Map();
  e.forEach((s) => {
    const { x: c, y: f, dataId: u } = s.setting.markSpec;
    n.has(c) || n.set(c, gt(u, c, t)), r.has(f) || r.set(f, gt(u, f, t));
  });
  const i = Array.from(n.values()), a = Array.from(r.values());
  function o(s, c) {
    const { type: f, axisLevel: u } = c, d = f === "x" ? i[u] : a[u];
    return {
      ...s,
      ...d
    };
  }
  return {
    withAxisRange: o
  };
}
function pt(t, e) {
  const { x: n, y: r } = e, i = t.getFieldType(e.dataId, n), a = t.getFieldType(e.dataId, r);
  return {
    xAxis: { type: i === "number" ? "value" : "category" },
    yAxis: { type: a === "number" ? "value" : "category" }
  };
}
function gt(t, e, n) {
  const { globalModel: r, datasetModel: i } = n, a = r.getFieldType(t, e), o = i.getDataset(t, { field: e });
  if (a === "number") {
    const c = Math.min(...o.flat(), 0), f = Math.ceil(Math.max(...o.flat())), { step: u, niceMin: d, niceMax: p } = di(c, f);
    return { min: d, max: p, interval: u };
  }
  return { data: Array.from(new Set(o.flat())) };
}
function hi(t) {
  t = Hr(t);
  const e = Yr(t), n = kr(t, e), r = fi({
    specCollector: t,
    gridModels: n,
    globalModel: e
  }), i = Jr({
    specCollector: t,
    seriesModels: r
  }), a = pi({
    seriesModels: r,
    datasetModel: i,
    globalModel: e
  }), o = {
    dataset: i.getDatasetOption(),
    grid: xi(n),
    series: yi(
      r,
      i,
      a
    ),
    xAxis: a.getXAxisOption(),
    yAxis: a.getYAxisOption()
  };
  return Nr(
    o,
    t.echartsOptionSpec || {},
    (s, c) => {
      if (Array.isArray(s) && !Array.isArray(c) && typeof c == "object")
        return Xr(s, Array(s.length).fill(c));
    }
  );
}
function xi(t) {
  return t.map((e) => e.getGridOption());
}
function yi(t, e, n) {
  return t.map((r, i) => {
    let a = r.getSeriesOption();
    return a = e.withDatasetIndex(i, a), a = n.withAxisIndex(i, a), a;
  });
}
function ht(t, e) {
  return mt.init(t, e.theme, e.initOptions);
}
function mi(t, e, n) {
  yt(
    () => n.resizeOption,
    (r, i, a) => {
      let o = null;
      if (r) {
        const { offsetWidth: s, offsetHeight: c } = t, { throttle: f = 100 } = r;
        let u = !1;
        const d = () => {
          e.resize();
        }, p = f ? mt.throttle(d, f) : d;
        o = new ResizeObserver(() => {
          !u && (u = !0, t.offsetWidth === s && t.offsetHeight === c) || p();
        }), o.observe(t);
      }
      a(() => {
        o && (o.disconnect(), o = null);
      });
    },
    { deep: !0, immediate: !0 }
  );
}
function xt(t, e, n) {
  t.setOption(n || {}, e.updateOptions || {});
}
function vi(t, e, n) {
  const { chartEvents: r, zrEvents: i } = n;
  r && r.forEach((a) => {
    t.on(a, (...o) => {
      if (o.length > 0) {
        const s = o[0];
        delete s.event, delete s.$vars;
      }
      e(`chart:${a}`, ...o);
    });
  }), i && i.forEach((a) => {
    t.getZr().on(a, (...o) => e(`zr:${a}`, ...o));
  });
}
function _i(t, e) {
  return Ht(() => {
    if (t.optionType === "dict")
      return t.option;
    const n = t.option;
    return n.refSets?.forEach((i) => {
      const { path: a, ref: o } = i;
      Lr(n, a, e.getVueRefObject(o).value);
    }), hi(n);
  });
}
const Ai = /* @__PURE__ */ Vt({
  __name: "echarts",
  props: {
    option: {},
    optionType: {},
    theme: {},
    initOptions: {},
    resizeOption: {},
    updateOptions: {},
    chartEvents: {},
    zrEvents: {}
  },
  setup(t, { emit: e }) {
    const n = t, r = Yt("root"), i = Kt(), a = e, o = te(), s = _i(n, o);
    Wt(() => {
      r.value && (i.value = ht(r.value, n), mi(r.value, i.value, n), xt(i.value, n, s.value), vi(i.value, a, n));
    }), yt(
      s,
      (f) => {
        !i.value && r.value && (i.value = ht(r.value, n)), xt(i.value, n, f);
      },
      { deep: !0 }
    );
    const c = Zt();
    return (f, u) => (Jt(), qt("div", Qt({ ref: "root" }, kt(c)), null, 16));
  }
});
export {
  Ai as default
};
