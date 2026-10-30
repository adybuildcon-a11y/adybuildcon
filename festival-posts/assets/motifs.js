/* Shared vector motifs for Osho festival creatives (diya, lantern, rangoli, bow, kalash, drapes ...). */
/* ------------------------------------------------------------------ helpers */
let uid = 0;
const id = p => `${p}${++uid}`;
const rnd = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();

function glow(cx, cy, r, color, op = .6) {
  const g = id('gl');
  return `<defs><radialGradient id="${g}"><stop offset="0" stop-color="${color}" stop-opacity="${op}"/>
    <stop offset=".45" stop-color="${color}" stop-opacity="${op * .35}"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></radialGradient></defs>
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#${g})"/>`;
}

function flame(x, y, s = 1) {
  const g = id('fl'), g2 = id('fi');
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <defs><linearGradient id="${g}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FF7A1A"/><stop offset=".55" stop-color="#FFB627"/><stop offset="1" stop-color="#FFE9A8"/></linearGradient>
    <linearGradient id="${g2}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FFF6D6"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient></defs>
    ${glow(0, -22, 70, '#FFB547', .55)}
    <path d="M0,0 C-15,-10 -14,-32 0,-58 C14,-32 15,-10 0,0Z" fill="url(#${g})"/>
    <path d="M0,-4 C-6,-10 -6,-22 0,-34 C6,-22 6,-10 0,-4Z" fill="url(#${g2})"/></g>`;
}

function diya(x, y, s = 1, body = ['#C2571E', '#7A2E0E'], rim = '#E7B04A') {
  const g = id('dy');
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <defs><linearGradient id="${g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${body[0]}"/><stop offset="1" stop-color="${body[1]}"/></linearGradient></defs>
    <ellipse cx="0" cy="46" rx="62" ry="7" fill="#000" opacity=".25"/>
    <path d="M-70,0 C-62,34 -30,46 0,46 C30,46 62,34 70,0 C40,-8 -40,-8 -70,0Z" fill="url(#${g})"/>
    <path d="M-70,0 C-40,-8 40,-8 70,0 C40,8 -40,8 -70,0Z" fill="#3B1606"/>
    <path d="M-70,0 C-40,-8 40,-8 70,0" fill="none" stroke="${rim}" stroke-width="3"/>
    <path d="M-48,20 C-20,30 20,30 48,20" fill="none" stroke="${rim}" stroke-width="2.4" stroke-dasharray="2 7" stroke-linecap="round"/>
    <path d="M-58,10 C-28,20 28,20 58,10" fill="none" stroke="${rim}" stroke-width="1.6" opacity=".7"/>
    ${flame(0, -4, 1)}</g>`;
}

function toran(width, y = 0, seg = 6, depth = 70) {
  let out = '';
  const step = width / seg;
  // string of mango leaves along the top
  for (let x = 12; x < width; x += 26) {
    out += `<path d="M${x},${y + 4} q-9,22 0,42 q9,-20 0,-42z" fill="${x % 52 < 26 ? '#2F7D4F' : '#3E9A5F'}" opacity=".95"/>`;
  }
  out += `<line x1="0" y1="${y + 4}" x2="${width}" y2="${y + 4}" stroke="#C98A2C" stroke-width="3"/>`;
  for (let i = 0; i < seg; i++) {
    const x0 = i * step, x1 = x0 + step, cx = x0 + step / 2;
    for (let t = 0; t <= 1.0001; t += 1 / 14) {
      const px = (1 - t) * (1 - t) * x0 + 2 * (1 - t) * t * cx + t * t * x1;
      const py = y + 18 + 2 * (1 - t) * t * depth * 2 * .5 * 2;
      const c = Math.round(t * 14) % 2 ? '#F7A21B' : '#E9690F';
      out += `<circle cx="${px}" cy="${py}" r="11" fill="${c}"/><circle cx="${px}" cy="${py}" r="4" fill="#9C3A06" opacity=".55"/>`;
    }
    if (i) {   // hanging drop
      out += `<line x1="${x0}" y1="${y + 18}" x2="${x0}" y2="${y + 70}" stroke="#E9690F" stroke-width="2"/>
        <circle cx="${x0}" cy="${y + 76}" r="10" fill="#F7A21B"/><circle cx="${x0}" cy="${y + 96}" r="8" fill="#E9690F"/>
        <path d="M${x0 - 6},${y + 104} l6,16 l6,-16z" fill="#C98A2C"/>`;
    }
  }
  return out;
}

function lantern(x, y, len, s = 1, c1 = '#E20886', c2 = '#F4B740') {
  const g = id('ln');
  return `<line x1="${x}" y1="0" x2="${x}" y2="${y}" stroke="#C98A2C" stroke-width="2"/>
  <g transform="translate(${x} ${y}) scale(${s})">
    <defs><linearGradient id="${g}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${c1}"/><stop offset=".5" stop-color="${c2}"/><stop offset="1" stop-color="${c1}"/></linearGradient></defs>
    ${glow(0, 70, 120, '#FFB547', .35)}
    <path d="M-14,0 h28 l26,34 h-80z" fill="#C98A2C"/>
    <path d="M-40,34 h80 l14,40 l-14,40 h-80 l-14,-40z" fill="url(#${g})" opacity=".95"/>
    <path d="M-40,34 l-14,40 l14,40 M40,34 l14,40 l-14,40 M0,34 v80 M-20,34 l-6,40 l6,40 M20,34 l6,40 l-6,40" stroke="#7A1B4A" stroke-width="1.6" fill="none" opacity=".6"/>
    <path d="M-40,114 h80 l-26,30 h-28z" fill="#C98A2C"/>
    ${[-12, -4, 4, 12].map(t => `<path d="M${t},144 v${len}" stroke="${t % 8 ? c2 : c1}" stroke-width="3"/>`).join('')}
  </g>`;
}

function rangoli(cx, cy, R, colors) {
  let out = `<g transform="translate(${cx} ${cy})" opacity=".9">`;
  const rings = [[R, 24, R * .2, colors[0]], [R * .78, 16, R * .2, colors[1]], [R * .56, 12, R * .17, colors[2]], [R * .36, 8, R * .14, colors[3]]];
  out += `<circle r="${R + 18}" fill="none" stroke="${colors[1]}" stroke-width="2" stroke-dasharray="3 9" opacity=".7"/>`;
  for (const [r, n, pl, c] of rings) {
    for (let i = 0; i < n; i++) {
      const a = i * 360 / n;
      out += `<path transform="rotate(${a}) translate(0 ${-r + pl})" d="M0,0 C${pl * .45},${-pl * .4} ${pl * .3},${-pl * .9} 0,${-pl} C${-pl * .3},${-pl * .9} ${-pl * .45},${-pl * .4} 0,0Z" fill="${c}" opacity=".9"/>`;
    }
    out += `<circle r="${r - pl - 6}" fill="none" stroke="${c}" stroke-width="1.5" opacity=".6"/>`;
  }
  return out + '</g>';
}

function bow(x, y, s, rot, gold = '#E7B04A', string = '#F6EEDC', withFlame = true, fletch = '#E20886') {
  const g = id('bw');
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">
    <defs><linearGradient id="${g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE3A0"/><stop offset=".5" stop-color="${gold}"/><stop offset="1" stop-color="#9A6516"/></linearGradient></defs>
    <path d="M-30,-262 L-104,0 L-30,262" fill="none" stroke="${string}" stroke-width="2.4"/>
    <path d="M-44,-268 C-30,-284 -6,-276 -2,-258 C14,-232 120,-150 122,0 C120,150 14,232 -2,258 C-6,276 -30,284 -44,268"
          fill="none" stroke="url(#${g})" stroke-width="13" stroke-linecap="round"/>
    <path d="M-2,-258 C14,-232 120,-150 122,0 C120,150 14,232 -2,258" fill="none" stroke="#FFF2C9" stroke-width="2" opacity=".55"/>
    <rect x="111" y="-30" width="22" height="60" rx="5" fill="#8E1B3E"/><path d="M111,-20 h22 M111,-6 h22 M111,8 h22 M111,22 h22" stroke="${gold}" stroke-width="2"/>
    <line x1="-104" y1="0" x2="304" y2="0" stroke="${gold}" stroke-width="6"/><line x1="-104" y1="-1.5" x2="300" y2="-1.5" stroke="#FFF2C9" stroke-width="1.4" opacity=".6"/>
    <path d="M300,-15 L346,0 L300,15 L310,0Z" fill="${gold}"/>
    <path d="M-104,0 l-26,-20 h34 l20,20 l-20,20 h-34z" fill="${fletch}" opacity=".9"/>
    <path d="M-78,0 l-22,-14 M-78,0 l-22,14 M-90,0 l-22,-14 M-90,0 l-22,14" stroke="#FFD1E8" stroke-width="1.6"/>
    ${withFlame ? `<g transform="translate(352 0) rotate(90)">${flame(0, 0, 1.1)}</g>` : ''}
  </g>`;
}

function rays(cx, cy, r0, r1, n, color, op) {
  let out = `<g opacity="${op}">`;
  for (let i = 0; i < n; i++) {
    const a = i * 2 * Math.PI / n, a2 = a + Math.PI / n * .35;
    out += `<path d="M${cx + r0 * Math.cos(a)},${cy + r0 * Math.sin(a)} L${cx + r1 * Math.cos(a)},${cy + r1 * Math.sin(a)} L${cx + r1 * Math.cos(a2)},${cy + r1 * Math.sin(a2)}Z" fill="${color}"/>`;
  }
  return out + '</g>';
}

function coin(x, y, r, tilt = .42) {
  const g = id('cn');
  return `<g transform="translate(${x} ${y})">
    <defs><linearGradient id="${g}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFE7A0"/><stop offset=".5" stop-color="#E2AE45"/><stop offset="1" stop-color="#A26D1B"/></linearGradient></defs>
    <ellipse cx="0" cy="${r * tilt * .35}" rx="${r}" ry="${r * tilt}" fill="#8A5A14"/>
    <ellipse cx="0" cy="0" rx="${r}" ry="${r * tilt}" fill="url(#${g})"/>
    <ellipse cx="0" cy="0" rx="${r * .74}" ry="${r * tilt * .74}" fill="none" stroke="#9A6516" stroke-width="1.6" opacity=".7"/></g>`;
}

function coinStack(x, y, r, n) {
  let out = '';
  for (let i = 0; i < n; i++) out += coin(x, y - i * r * .19, r);
  return out;
}

function kalash(x, y, s = 1) {
  const g = id('ks'), g2 = id('kc');
  let leaves = '';
  for (let i = -2; i <= 2; i++) {
    leaves += `<path transform="rotate(${i * 22} 0 -128)" d="M0,-128 C-16,-160 -12,-205 0,-232 C12,-205 16,-160 0,-128Z" fill="${i % 2 ? '#2F7D4F' : '#3E9A5F'}"/>
      <path transform="rotate(${i * 22} 0 -128)" d="M0,-132 V-226" stroke="#1F5E39" stroke-width="1.5"/>`;
  }
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <defs><linearGradient id="${g}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8A5A14"/><stop offset=".3" stop-color="#F2C766"/><stop offset=".55" stop-color="#E2AE45"/><stop offset="1" stop-color="#7A4E10"/></linearGradient>
    <radialGradient id="${g2}" cx=".4" cy=".35"><stop offset="0" stop-color="#9B6A3A"/><stop offset="1" stop-color="#4E2E14"/></radialGradient></defs>
    ${glow(0, -20, 300, '#FFC766', .28)}
    ${leaves}
    <ellipse cx="0" cy="-178" rx="44" ry="56" fill="url(#${g2})"/>
    <path d="M-28,-212 q28,-30 56,0" fill="none" stroke="#C9A06A" stroke-width="3"/>
    <path d="M-44,-140 C-44,-104 -132,-84 -132,2 C-132,78 -74,116 -60,126 L60,126 C74,116 132,78 132,2 C132,-84 44,-104 44,-140Z" fill="url(#${g})"/>
    <ellipse cx="0" cy="-140" rx="66" ry="14" fill="#E2AE45" stroke="#8A5A14" stroke-width="2"/>
    <path d="M-120,-36 C-60,-20 60,-20 120,-36" fill="none" stroke="#B3122E" stroke-width="7"/>
    <path d="M-131,-8 C-60,8 60,8 131,-8" fill="none" stroke="#B3122E" stroke-width="4"/>
    <text x="0" y="56" text-anchor="middle" font-family="Tiro" font-size="60" fill="#B3122E">श्री</text>
    <ellipse cx="0" cy="128" rx="64" ry="10" fill="#7A4E10"/></g>`;
}

function arch(x0, y0, x1, y1) {     // rectangle with a semicircular top
  const r = (x1 - x0) / 2;
  return `M${x0},${y1} L${x0},${y0 + r} A${r},${r} 0 0 1 ${x1},${y0 + r} L${x1},${y1} Z`;
}

function drapes(top, bottom, base = '#1F2A44', dark = '#121A2E', light = '#34416A', trim = '#B8923F') {
  const gL = id('dr'), gR = id('dr');
  const folds = (gid, flip) => {
    let stops = '';
    const n = 9;
    for (let i = 0; i <= n; i++) {
      const o = i / n;
      stops += `<stop offset="${o}" stop-color="${i % 2 ? light : dark}"/>`;
      if (i < n) stops += `<stop offset="${o + .5 / n}" stop-color="${base}"/>`;
    }
    return `<linearGradient id="${gid}" x1="${flip ? 1 : 0}" y1="0" x2="${flip ? 0 : 1}" y2="0">${stops}</linearGradient>`;
  };
  const tie = top + (bottom - top) * .56;
  const L = `M0,${top} L250,${top} C230,${top + 200} 150,${tie - 150} 118,${tie} C140,${tie + 90} 200,${bottom - 120} 214,${bottom} L0,${bottom} Z`;
  const R = `M${W},${top} L${W - 250},${top} C${W - 230},${top + 200} ${W - 150},${tie - 150} ${W - 118},${tie} C${W - 140},${tie + 90} ${W - 200},${bottom - 120} ${W - 214},${bottom} L${W},${bottom} Z`;
  // valance with swags
  let val = `<rect x="0" y="0" width="${W}" height="${top + 30}" fill="${base}"/>`;
  const sw = 5, step = W / sw;
  let swag = `M0,${top + 30}`;
  for (let i = 0; i < sw; i++) swag += ` Q${i * step + step / 2},${top + 110} ${(i + 1) * step},${top + 30}`;
  val += `<path d="${swag} L${W},0 L0,0Z" fill="${base}"/>`;
  val += `<path d="${swag}" fill="none" stroke="${trim}" stroke-width="5"/>`;
  val += `<path d="${swag.replace(/(\d+\.?\d*),(\d+\.?\d*)/g, (m, a, b) => `${a},${+b + 12}`)}" fill="none" stroke="${trim}" stroke-width="2" stroke-dasharray="2 6" opacity=".9"/>`;
  for (let i = 1; i < sw; i++) val += `<circle cx="${i * step}" cy="${top + 32}" r="11" fill="${trim}"/><path d="M${i * step - 7},${top + 40} l7,40 l7,-40z" fill="${trim}"/>`;
  return `<defs>${folds(gL, false)}${folds(gR, true)}</defs>
    <path d="${L}" fill="url(#${gL})"/><path d="${R}" fill="url(#${gR})"/>
    <path d="M250,${top} C230,${top + 200} 150,${tie - 150} 118,${tie} C140,${tie + 90} 200,${bottom - 120} 214,${bottom}" fill="none" stroke="${trim}" stroke-width="3"/>
    <path d="M${W - 250},${top} C${W - 230},${top + 200} ${W - 150},${tie - 150} ${W - 118},${tie} C${W - 140},${tie + 90} ${W - 200},${bottom - 120} ${W - 214},${bottom}" fill="none" stroke="${trim}" stroke-width="3"/>
    <rect x="-4" y="${tie - 16}" width="130" height="30" rx="14" fill="${trim}"/><circle cx="126" cy="${tie - 1}" r="16" fill="#D8B66A" stroke="#7E5C1C" stroke-width="2"/>
    <rect x="${W - 126}" y="${tie - 16}" width="130" height="30" rx="14" fill="${trim}"/><circle cx="${W - 126}" cy="${tie - 1}" r="16" fill="#D8B66A" stroke="#7E5C1C" stroke-width="2"/>
    ${val}`;
}

function sparkle(x, y, r, c, op = 1) {
  return `<path d="M${x},${y - r} Q${x},${y} ${x + r},${y} Q${x},${y} ${x},${y + r} Q${x},${y} ${x - r},${y} Q${x},${y} ${x},${y - r}Z" fill="${c}" opacity="${op}"/>`;
}

function firework(cx, cy, r, c, n = 28) {
  let out = `<g opacity=".85">`;
  for (let i = 0; i < n; i++) {
    const a = i * 2 * Math.PI / n;
    out += `<line x1="${cx + r * .25 * Math.cos(a)}" y1="${cy + r * .25 * Math.sin(a)}" x2="${cx + r * Math.cos(a)}" y2="${cy + r * Math.sin(a)}" stroke="${c}" stroke-width="2" stroke-linecap="round"/>
            <circle cx="${cx + r * 1.08 * Math.cos(a)}" cy="${cy + r * 1.08 * Math.sin(a)}" r="2.6" fill="${c}"/>`;
  }
  return out + '</g>';
}

function stars(n, x0, y0, x1, y1, c) {
  let out = '';
  for (let i = 0; i < n; i++) out += `<circle cx="${x0 + rnd() * (x1 - x0)}" cy="${y0 + rnd() * (y1 - y0)}" r="${.8 + rnd() * 1.8}" fill="${c}" opacity="${.3 + rnd() * .6}"/>`;
  return out;
}

