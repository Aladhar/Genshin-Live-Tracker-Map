import {
  offlineAreaList,
  offlineIcons,
  offlineItems,
  offlineItemTypes,
  offlineMarkers,
} from "./local_mondstadt_data";

function page_record(record) {
  return {
    data: {
      data: {
        record,
      },
    },
  };
}

function matching_markers(itemIdList = []) {
  if (!itemIdList.length) {
    return offlineMarkers;
  }
  const wanted = new Set(itemIdList);
  return offlineMarkers.filter((marker) =>
    marker.itemList.some((item) => wanted.has(item.itemId)),
  );
}

function offline_response(url, data = {}) {
  if (url === "/area/get/list") {
    return { data: { data: offlineAreaList } };
  }
  if (url.startsWith("/item_type/get/list")) {
    return page_record(offlineItemTypes);
  }
  if (url === "/item/get/list") {
    const areaIds = data?.areaIdList || [];
    const record = areaIds.length
      ? offlineItems.filter((item) => areaIds.includes(item.areaId))
      : offlineItems;
    return page_record(record);
  }
  if (url === "/icon/get/list") {
    return page_record(offlineIcons);
  }
  if (url === "/marker/get/list_byinfo") {
    return { data: { data: matching_markers(data?.itemIdList || []) } };
  }
  if (url === "/marker/get/list_byid") {
    const wanted = new Set(data?.markerIdList || []);
    return {
      data: {
        data: offlineMarkers.filter((marker) => wanted.has(marker.id)),
      },
    };
  }
  return { data: { data: {} } };
}

function default_request(url, data) {
  return Promise.resolve(offline_response(url, data));
}
/**
 * 列出地区
 * @param {Number} parentId 父级ID,默认为-1
 * @param {Boolean} isTraverse 是否遍历子地区
 * @returns 地区信息
 */
function query_area(data) {
  return default_request("/area/get/list", data);
}
/**
 * 列出物品类型
 * @param {Number} self 查询自身还是查询子级，0为查询自身，1为查询子级
 * @param {Array} typeIdList 父级类型ID列表
 * @param {Number} current 当前页，从0开始
 * @param {Number} size 每页大小，默认为10
 * @returns 物品类型信息
 */
function query_type(self, data) {
  return default_request(`/item_type/get/list/${self}`, data);
}
/**
 * 列出物品列表
 * @param {Array} typeIdList 末端物品类型ID列表
 * @param {Array} areaIdList 末端地区ID列表
 * @param {Number} current 当前页，从0开始
 * @param {Number} size 每页大小，默认为10
 * @returns 物品列表信息
 */
function query_itemlist(data) {
  return default_request(`/item/get/list`, data);
}
/**
 * 列出物品信息列表
 * @param {Array} typeIdList 物品类型ID列表
 * @param {Array} areaIdList 地区ID列表
 * @param {Array} itemIdList 物品ID列表
 * @param {Number} getBeta 获取测试点位,默认为0，不获取，为1时只获取测试点
 * @returns 物品点位id信息
 */
function query_itemlayer_infolist(data) {
  return default_request(`/marker/get/list_byinfo`, data);
}
/**
 * 按id列表查询点位信息
 * @param {Array} data 物品类型ID列表
 * @returns 物品点位id信息
 */
function query_itemlayer_byid(data) {
  return default_request(`/marker/get/list_byid`, data);
}
/**
 * 列出所有标签
 * @param {Array} tagList 标签名列表
 * @param {Array} typeIdList 图标标签分类列表
 * @returns 物品点位图标信息
 */
function query_iconlist(data) {
  return default_request(`/icon/get/list`, data);
}
function clear_cache() {
  return default_request(`/cache/item`, undefined, "delete");
}
export {
  query_area,
  query_type,
  query_itemlist,
  query_itemlayer_infolist,
  query_iconlist,
  query_itemlayer_byid,
  clear_cache,
};
