import { p as y } from "./chunk-353BL4L5-D4dVjjbU.js";
import { C as B, s as S, g as z, n as E, o as F, b as P, c as W, _ as i, l as w, D as x, E as D, t as T, H as _, k as A } from "./mermaid.core-D36e06XD.js";
import { p as N } from "./treemap-FKARHQ26-2Ty0RcZX.js";
var m = {
  packet: []
}, v = structuredClone(m), L = B.packet, Y = /* @__PURE__ */ i(() => {
  const t = x({
    ...L,
    ...D().packet
  });
  return t.showBits && (t.paddingY += 10), t;
}, "getConfig"), H = /* @__PURE__ */ i(() => v.packet, "getPacket"), I = /* @__PURE__ */ i((t) => {
  t.length > 0 && v.packet.push(t);
}, "pushWord"), M = /* @__PURE__ */ i(() => {
  T(), v = structuredClone(m);
}, "clear"), u = {
  pushWord: I,
  getPacket: H,
  getConfig: Y,
  clear: M,
  setAccTitle: S,
  getAccTitle: z,
  setDiagramTitle: E,
  getDiagramTitle: F,
  getAccDescription: P,
  setAccDescription: W
}, O = 1e4, G = /* @__PURE__ */ i((t) => {
  y(t, u);
  let e = -1, o = [], n = 1;
  const { bitsPerRow: s } = u.getConfig();
  for (let { start: a, end: r, bits: c, label: f } of t.blocks) {
    if (a !== void 0 && r !== void 0 && r < a)
      throw new Error(`Packet block ${a} - ${r} is invalid. End must be greater than start.`);
    if (a ??= e + 1, a !== e + 1)
      throw new Error(
        `Packet block ${a} - ${r ?? a} is not contiguous. It should start from ${e + 1}.`
      );
    if (c === 0)
      throw new Error(`Packet block ${a} is invalid. Cannot have a zero bit field.`);
    for (r ??= a + (c ?? 1) - 1, c ??= r - a + 1, e = r, w.debug(`Packet block ${a} - ${e} with label ${f}`); o.length <= s + 1 && u.getPacket().length < O; ) {
      const [d, p] = K({ start: a, end: r, bits: c, label: f }, n, s);
      if (o.push(d), d.end + 1 === n * s && (u.pushWord(o), o = [], n++), !p)
        break;
      ({ start: a, end: r, bits: c, label: f } = p);
    }
  }
  u.pushWord(o);
}, "populate"), K = /* @__PURE__ */ i((t, e, o) => {
  if (t.start === void 0)
    throw new Error("start should have been set during first phase");
  if (t.end === void 0)
    throw new Error("end should have been set during first phase");
  if (t.start > t.end)
    throw new Error(`Block start ${t.start} is greater than block end ${t.end}.`);
  if (t.end + 1 <= e * o)
    return [t, void 0];
  const n = e * o - 1, s = e * o;
  return [
    {
      start: t.start,
      end: n,
      label: t.label,
      bits: n - t.start
    },
    {
      start: s,
      end: t.end,
      label: t.label,
      bits: t.end - s
    }
  ];
}, "getNextFittingBlock"), R = {
  parse: /* @__PURE__ */ i(async (t) => {
    const e = await N("packet", t);
    w.debug(e), G(e);
  }, "parse")
}, U = /* @__PURE__ */ i((t, e, o, n) => {
  const s = n.db, a = s.getConfig(), { rowHeight: r, paddingY: c, bitWidth: f, bitsPerRow: d } = a, p = s.getPacket(), l = s.getDiagramTitle(), k = r + c, g = k * (p.length + 1) - (l ? 0 : r), b = f * d + 2, h = _(e);
  h.attr("viewbox", `0 0 ${b} ${g}`), A(h, g, b, a.useMaxWidth);
  for (const [C, $] of p.entries())
    X(h, $, C, a);
  h.append("text").text(l).attr("x", b / 2).attr("y", g - k / 2).attr("dominant-baseline", "middle").attr("text-anchor", "middle").attr("class", "packetTitle");
}, "draw"), X = /* @__PURE__ */ i((t, e, o, { rowHeight: n, paddingX: s, paddingY: a, bitWidth: r, bitsPerRow: c, showBits: f }) => {
  const d = t.append("g"), p = o * (n + a) + a;
  for (const l of e) {
    const k = l.start % c * r + 1, g = (l.end - l.start + 1) * r - s;
    if (d.append("rect").attr("x", k).attr("y", p).attr("width", g).attr("height", n).attr("class", "packetBlock"), d.append("text").attr("x", k + g / 2).attr("y", p + n / 2).attr("class", "packetLabel").attr("dominant-baseline", "middle").attr("text-anchor", "middle").text(l.label), !f)
      continue;
    const b = l.end === l.start, h = p - 2;
    d.append("text").attr("x", k + (b ? g / 2 : 0)).attr("y", h).attr("class", "packetByte start").attr("dominant-baseline", "auto").attr("text-anchor", b ? "middle" : "start").text(l.start), b || d.append("text").attr("x", k + g).attr("y", h).attr("class", "packetByte end").attr("dominant-baseline", "auto").attr("text-anchor", "end").text(l.end);
  }
}, "drawWord"), j = { draw: U }, q = {
  byteFontSize: "10px",
  startByteColor: "black",
  endByteColor: "black",
  labelColor: "black",
  labelFontSize: "12px",
  titleColor: "black",
  titleFontSize: "14px",
  blockStrokeColor: "black",
  blockStrokeWidth: "1",
  blockFillColor: "#efefef"
}, J = /* @__PURE__ */ i(({ packet: t } = {}) => {
  const e = x(q, t);
  return `
	.packetByte {
		font-size: ${e.byteFontSize};
	}
	.packetByte.start {
		fill: ${e.startByteColor};
	}
	.packetByte.end {
		fill: ${e.endByteColor};
	}
	.packetLabel {
		fill: ${e.labelColor};
		font-size: ${e.labelFontSize};
	}
	.packetTitle {
		fill: ${e.titleColor};
		font-size: ${e.titleFontSize};
	}
	.packetBlock {
		stroke: ${e.blockStrokeColor};
		stroke-width: ${e.blockStrokeWidth};
		fill: ${e.blockFillColor};
	}
	`;
}, "styles"), tt = {
  parser: R,
  db: u,
  renderer: j,
  styles: J
};
export {
  tt as diagram
};
