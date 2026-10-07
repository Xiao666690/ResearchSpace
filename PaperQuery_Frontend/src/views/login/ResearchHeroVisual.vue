<template>
  <svg
    class="research-visual"
    viewBox="0 0 620 500"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <defs>
      <linearGradient
        id="paper-front"
        x1="224"
        y1="130"
        x2="420"
        y2="394"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#fff" />
        <stop offset="1" stop-color="#f1efff" />
      </linearGradient>
      <linearGradient
        id="paper-back"
        x1="125"
        y1="100"
        x2="415"
        y2="470"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#fff" stop-opacity=".96" />
        <stop offset="1" stop-color="#ddd9ff" stop-opacity=".84" />
      </linearGradient>
      <linearGradient
        id="orbit"
        x1="70"
        y1="390"
        x2="562"
        y2="160"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#fff" stop-opacity=".25" />
        <stop offset=".38" stop-color="#b9a9ff" />
        <stop offset=".76" stop-color="#7560f4" />
        <stop offset="1" stop-color="#b0a0fb" />
      </linearGradient>
      <radialGradient id="node">
        <stop stop-color="#fdfbff" />
        <stop offset=".52" stop-color="#aa91ff" />
        <stop offset="1" stop-color="#5535ea" />
      </radialGradient>
      <filter id="blur"><feGaussianBlur stdDeviation="27" /></filter>
      <filter id="paper-shadow" x="-50%" y="-50%" width="200%" height="200%">
        <feDropShadow
          dx="0"
          dy="22"
          stdDeviation="19"
          flood-color="#5848c8"
          flood-opacity=".21"
        />
      </filter>
      <filter id="node-glow" x="-200%" y="-200%" width="500%" height="500%">
        <feGaussianBlur stdDeviation="9" />
      </filter>
      <pattern id="lines" width="92" height="17" patternUnits="userSpaceOnUse">
        <path
          d="M0 5H76M0 11H86"
          stroke="#aaa9e8"
          stroke-opacity=".52"
          stroke-width="2"
        />
      </pattern>
    </defs>
    <ellipse
      cx="331"
      cy="325"
      rx="207"
      ry="90"
      fill="#8b77ef"
      opacity=".25"
      filter="url(#blur)"
    />
    <g
      class="paper paper-back-left"
      filter="url(#paper-shadow)"
      transform="translate(128 167) rotate(-18 90 141)"
    >
      <rect width="176" height="282" rx="5" fill="url(#paper-back)" />
      <path
        d="M23 33H74M23 44H120M23 55H108"
        stroke="#aca8e9"
        stroke-opacity=".72"
        stroke-width="3"
      />
      <rect
        x="23"
        y="76"
        width="130"
        height="164"
        fill="url(#lines)"
        opacity=".8"
      />
    </g>
    <g
      class="paper paper-back-right"
      filter="url(#paper-shadow)"
      transform="translate(291 109) rotate(11 84 153)"
    >
      <rect width="168" height="306" rx="5" fill="url(#paper-back)" />
      <path
        d="M20 37H69M20 49H128M20 61H111"
        stroke="#b5b2ed"
        stroke-opacity=".8"
        stroke-width="3"
      />
      <rect
        x="20"
        y="85"
        width="130"
        height="180"
        fill="url(#lines)"
        opacity=".8"
      />
    </g>
    <g
      class="paper paper-front"
      filter="url(#paper-shadow)"
      transform="translate(223 139) rotate(-8 101 153)"
    >
      <path
        d="M0 0H202L211 307H8L0 0Z"
        fill="url(#paper-front)"
        stroke="#fff"
        stroke-width="2"
      />
      <path
        d="M28 36H75"
        stroke="#b5b4f4"
        stroke-width="4"
        stroke-linecap="round"
      />
      <text class="paper-title" x="28" y="89" fill="#5f59bc">Research</text>
      <text class="paper-title" x="28" y="115" fill="#5f59bc">Paper</text>
      <path
        d="M29 143H119M29 151H153"
        stroke="#aaa4ef"
        stroke-width="3"
        stroke-linecap="round"
      />
      <rect
        x="29"
        y="170"
        width="149"
        height="97"
        fill="url(#lines)"
        opacity=".86"
      />
    </g>
    <ellipse
      cx="322"
      cy="276"
      rx="279"
      ry="87"
      transform="rotate(-28 322 276)"
      stroke="url(#orbit)"
      stroke-width="2"
    />
    <circle
      cx="115"
      cy="394"
      r="22"
      fill="#8c74f5"
      opacity=".4"
      filter="url(#node-glow)"
    />
    <circle cx="115" cy="394" r="14" fill="url(#node)" />
    <circle
      cx="506"
      cy="159"
      r="21"
      fill="#8c74f5"
      opacity=".4"
      filter="url(#node-glow)"
    />
    <circle cx="506" cy="159" r="14" fill="url(#node)" />
    <circle cx="560" cy="265" r="13" fill="url(#node)" />
  </svg>
</template>

<style scoped>
.research-visual {
  display: block;
  width: 100%;
  height: 100%;
  overflow: visible;
}
.paper-title {
  font-family: Georgia, serif;
  font-size: 25px;
}
@media (prefers-reduced-motion: no-preference) {
  .paper-front {
    animation: paper-drift 7s ease-in-out infinite;
  }
  .paper-back-left {
    animation: paper-drift 9s ease-in-out -2s infinite;
  }
  .paper-back-right {
    animation: paper-drift 8s ease-in-out -4s infinite;
  }
}
@keyframes paper-drift {
  50% {
    translate: 0 -8px;
  }
}
</style>
