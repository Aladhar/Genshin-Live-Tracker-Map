import axios from "axios";

const configUrl = "https://assets.yuanshen.site/webapp.json";

const localFallbackConfig = {
  webMap: {
    blockArea: [],
  },
  tiles: {
    mondstadt: {
      code: "twt642",
      center: [3568, 6969],
      size: [30370, 20480],
      tilesOffset: [-17408, -4096],
      settings: {
        center: [1438, -3333],
        zoom: 0,
      },
    },
  },
  plugins: {},
};

function fetch_config() {
  return axios
    .get(`${configUrl}?r=${Date.now()}`, { timeout: 10000 })
    .then((res) => {
      const config = res.data || {};
      if (config.webMap && config.tiles) {
        return config;
      }
      return localFallbackConfig;
    })
    .catch(() => localFallbackConfig);
}

export { fetch_config };
