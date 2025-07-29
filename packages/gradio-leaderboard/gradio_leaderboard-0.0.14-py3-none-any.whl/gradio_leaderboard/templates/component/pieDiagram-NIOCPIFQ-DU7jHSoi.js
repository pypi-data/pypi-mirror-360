import { p as U } from "./chunk-353BL4L5-D4dVjjbU.js";
import { ab as y, a3 as z, aG as j, C as H, n as Z, o as q, s as J, g as K, c as Q, b as X, _ as p, l as G, t as Y, d as tt, D as et, H as at, P as rt, k as nt } from "./mermaid.core-D36e06XD.js";
import { p as it } from "./treemap-FKARHQ26-2Ty0RcZX.js";
import { d as O } from "./arc-4UNMf6Jv.js";
import { o as st } from "./ordinal-DfAQgscy.js";
function ot(t, a) {
  return a < t ? -1 : a > t ? 1 : a >= t ? 0 : NaN;
}
function lt(t) {
  return t;
}
function ct() {
  var t = lt, a = ot, h = null, s = y(0), d = y(z), x = y(0);
  function i(e) {
    var r, l = (e = j(e)).length, c, A, m = 0, u = new Array(l), n = new Array(l), v = +s.apply(this, arguments), w = Math.min(z, Math.max(-z, d.apply(this, arguments) - v)), f, T = Math.min(Math.abs(w) / l, x.apply(this, arguments)), $ = T * (w < 0 ? -1 : 1), g;
    for (r = 0; r < l; ++r)
      (g = n[u[r] = r] = +t(e[r], r, e)) > 0 && (m += g);
    for (a != null ? u.sort(function(S, C) {
      return a(n[S], n[C]);
    }) : h != null && u.sort(function(S, C) {
      return h(e[S], e[C]);
    }), r = 0, A = m ? (w - l * $) / m : 0; r < l; ++r, v = f)
      c = u[r], g = n[c], f = v + (g > 0 ? g * A : 0) + $, n[c] = {
        data: e[c],
        index: r,
        value: g,
        startAngle: v,
        endAngle: f,
        padAngle: T
      };
    return n;
  }
  return i.value = function(e) {
    return arguments.length ? (t = typeof e == "function" ? e : y(+e), i) : t;
  }, i.sortValues = function(e) {
    return arguments.length ? (a = e, h = null, i) : a;
  }, i.sort = function(e) {
    return arguments.length ? (h = e, a = null, i) : h;
  }, i.startAngle = function(e) {
    return arguments.length ? (s = typeof e == "function" ? e : y(+e), i) : s;
  }, i.endAngle = function(e) {
    return arguments.length ? (d = typeof e == "function" ? e : y(+e), i) : d;
  }, i.padAngle = function(e) {
    return arguments.length ? (x = typeof e == "function" ? e : y(+e), i) : x;
  }, i;
}
var R = H.pie, F = {
  sections: /* @__PURE__ */ new Map(),
  showData: !1,
  config: R
}, E = F.sections, P = F.showData, ut = structuredClone(R), pt = /* @__PURE__ */ p(() => structuredClone(ut), "getConfig"), dt = /* @__PURE__ */ p(() => {
  E = /* @__PURE__ */ new Map(), P = F.showData, Y();
}, "clear"), gt = /* @__PURE__ */ p(({ label: t, value: a }) => {
  E.has(t) || (E.set(t, a), G.debug(`added new section: ${t}, with value: ${a}`));
}, "addSection"), ft = /* @__PURE__ */ p(() => E, "getSections"), ht = /* @__PURE__ */ p((t) => {
  P = t;
}, "setShowData"), mt = /* @__PURE__ */ p(() => P, "getShowData"), I = {
  getConfig: pt,
  clear: dt,
  setDiagramTitle: Z,
  getDiagramTitle: q,
  setAccTitle: J,
  getAccTitle: K,
  setAccDescription: Q,
  getAccDescription: X,
  addSection: gt,
  getSections: ft,
  setShowData: ht,
  getShowData: mt
}, vt = /* @__PURE__ */ p((t, a) => {
  U(t, a), a.setShowData(t.showData), t.sections.map(a.addSection);
}, "populateDb"), St = {
  parse: /* @__PURE__ */ p(async (t) => {
    const a = await it("pie", t);
    G.debug(a), vt(a, I);
  }, "parse")
}, yt = /* @__PURE__ */ p((t) => `
  .pieCircle{
    stroke: ${t.pieStrokeColor};
    stroke-width : ${t.pieStrokeWidth};
    opacity : ${t.pieOpacity};
  }
  .pieOuterCircle{
    stroke: ${t.pieOuterStrokeColor};
    stroke-width: ${t.pieOuterStrokeWidth};
    fill: none;
  }
  .pieTitleText {
    text-anchor: middle;
    font-size: ${t.pieTitleTextSize};
    fill: ${t.pieTitleTextColor};
    font-family: ${t.fontFamily};
  }
  .slice {
    font-family: ${t.fontFamily};
    fill: ${t.pieSectionTextColor};
    font-size:${t.pieSectionTextSize};
    // fill: white;
  }
  .legend text {
    fill: ${t.pieLegendTextColor};
    font-family: ${t.fontFamily};
    font-size: ${t.pieLegendTextSize};
  }
`, "getStyles"), xt = yt, At = /* @__PURE__ */ p((t) => {
  const a = [...t.entries()].map((s) => ({
    label: s[0],
    value: s[1]
  })).sort((s, d) => d.value - s.value);
  return ct().value(
    (s) => s.value
  )(a);
}, "createPieArcs"), wt = /* @__PURE__ */ p((t, a, h, s) => {
  G.debug(`rendering pie chart
` + t);
  const d = s.db, x = tt(), i = et(d.getConfig(), x.pie), e = 40, r = 18, l = 4, c = 450, A = c, m = at(a), u = m.append("g");
  u.attr("transform", "translate(" + A / 2 + "," + c / 2 + ")");
  const { themeVariables: n } = x;
  let [v] = rt(n.pieOuterStrokeWidth);
  v ??= 2;
  const w = i.textPosition, f = Math.min(A, c) / 2 - e, T = O().innerRadius(0).outerRadius(f), $ = O().innerRadius(f * w).outerRadius(f * w);
  u.append("circle").attr("cx", 0).attr("cy", 0).attr("r", f + v / 2).attr("class", "pieOuterCircle");
  const g = d.getSections(), S = At(g), C = [
    n.pie1,
    n.pie2,
    n.pie3,
    n.pie4,
    n.pie5,
    n.pie6,
    n.pie7,
    n.pie8,
    n.pie9,
    n.pie10,
    n.pie11,
    n.pie12
  ], D = st(C);
  u.selectAll("mySlices").data(S).enter().append("path").attr("d", T).attr("fill", (o) => D(o.data.label)).attr("class", "pieCircle");
  let W = 0;
  g.forEach((o) => {
    W += o;
  }), u.selectAll("mySlices").data(S).enter().append("text").text((o) => (o.data.value / W * 100).toFixed(0) + "%").attr("transform", (o) => "translate(" + $.centroid(o) + ")").style("text-anchor", "middle").attr("class", "slice"), u.append("text").text(d.getDiagramTitle()).attr("x", 0).attr("y", -(c - 50) / 2).attr("class", "pieTitleText");
  const M = u.selectAll(".legend").data(D.domain()).enter().append("g").attr("class", "legend").attr("transform", (o, k) => {
    const b = r + l, _ = b * D.domain().length / 2, B = 12 * r, V = k * b - _;
    return "translate(" + B + "," + V + ")";
  });
  M.append("rect").attr("width", r).attr("height", r).style("fill", D).style("stroke", D), M.data(S).append("text").attr("x", r + l).attr("y", r - l).text((o) => {
    const { label: k, value: b } = o.data;
    return d.getShowData() ? `${k} [${b}]` : k;
  });
  const L = Math.max(
    ...M.selectAll("text").nodes().map((o) => o?.getBoundingClientRect().width ?? 0)
  ), N = A + e + r + l + L;
  m.attr("viewBox", `0 0 ${N} ${c}`), nt(m, c, N, i.useMaxWidth);
}, "draw"), Ct = { draw: wt }, Et = {
  parser: St,
  db: I,
  renderer: Ct,
  styles: xt
};
export {
  Et as diagram
};
