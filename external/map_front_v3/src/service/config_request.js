import axios from "axios";

const localFallbackConfig = {
  webMap: {
    blockArea: [],
  },
  tiles: {
    "teyvat-main": {
      code: "genshin-mainmap",
      center: [14336, 12288],
      size: [25600, 34880],
      tilesOffset: [0, 0],
      imageManifest: "genshin-mainmap",
      imageBaseUrl: "/imgs/genshin-mainmap",
      settings: {
        center: [0, 0],
        zoom: -5,
        minZoom: -6,
        maxZoom: 1,
      },
    },
  },
  plugins: {},
};

function fetch_config() {
  if (import.meta.env.DEV) {
    return Promise.resolve(localFallbackConfig);
  }

  const url = `https://assets.yuanshen.site/webapp.json?r=${Math.random()}`;
  return axios
    .get(url, { timeout: 3000 })
    .then((res) => res.data || localFallbackConfig)
    .catch(() => localFallbackConfig);
}

export { fetch_config };
