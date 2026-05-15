import { boot } from "quasar/wrappers";

const exactTranslations = new Map([
  ["原神地图-v3", "Genshin Map v3"],
  ["更换地区", "Change Region"],
  ["更换地图", "Change Map"],
  ["传送点位", "Teleport Points"],
  ["标记点位", "Marked Points"],
  ["仅显示分层点位", "Layered Points Only"],
  ["功能菜单", "Menu"],
  ["加入讨论组", "Join Discussion"],
  ["反馈/建议", "Feedback"],
  ["下载客户端", "Download Client"],
  ["登录", "Log In"],
  ["存档", "Saves"],
  ["存档(有改动尚未保存)", "Saves (unsaved changes)"],
  ["调试", "Debug"],
  ["清除所有", "Clear All"],
  ["宝箱", "Chests"],
  ["宝箱品质", "Chest Quality"],
  ["宝箱形式", "Chest Type"],
  ["选择分层层级", "Select Layer"],
  ["没有相关图片", "No images available"],
  ["点击播放视频", "Play video"],
  ["未完成", "Incomplete"],
  ["已完成", "Complete"],
  ["存档列表", "Saves"],
  ["新建存档", "New Save"],
  ["保存", "Save"],
  ["注销", "Log Out"],
  ["激活中", "Active"],
  ["未激活", "Inactive"],
  ["重命名", "Rename"],
  ["读档", "Load"],
  ["删除存档", "Delete Save"],
  ["创建时间", "Created"],
  ["最后修改时间", "Last Modified"],
  ["最后更新时间", "Last Updated"],
  ["操作", "Actions"],
  ["状态", "Status"],
  ["存档名称", "Save Name"],
  ["解决存档冲突", "Resolve Save Conflict"],
  ["本地存档", "Local Save"],
  ["云端存档", "Cloud Save"],
  ["关闭", "Close"],
  ["免责声明", "Disclaimer"],
  ["招募", "Join"],
  ["更新日志", "Changelog"],
  ["前往下载", "Download"],
  ["浏览旧版地图", "Open Old Map"],
  ["试用测试版", "Open Beta"],
  ["网页地图正在施工中", "The web map is under construction"],
  ["这是你没使用过的船新版本", "A redesigned version is in progress"],
  ["或者，不妨来试试全新的", "Or try the new"],
  ["3.1地图客户端版本", "Map Client 3.1"],
  ["3.0地图客户端版本", "Map Client 3.0"],
  ["新的存档", "New Save"],
  ["保存成功！", "Saved."],
  ["读取成功", "Loaded."],
  ["自动存档中，请稍后", "Auto-saving, please wait"],
  ["同步数据中，请稍后", "Syncing data, please wait"],
  ["链接失败，请稍后重试", "Connection failed. Try again later."],
  ["输入秘笈成功！开启隐藏模式！", "Secret code accepted. Hidden mode enabled."],
  ["输入秘笈成功！关闭隐藏模式！", "Secret code accepted. Hidden mode disabled."],
  ["七天神像", "Statue of The Seven"],
  ["传送锚点", "Teleport Waypoint"],
  ["秘境", "Domain"],
  ["征讨领域", "Trounce Domain"],
  ["浪船锚点", "Waverider Waypoint"],
  ["奖励秘境", "Reward Domain"],
]);

const phraseTranslations = [
  ["创建时间：", "Created: "],
  ["最后更新时间:", "Last updated: "],
  ["最后修改时间：", "Last modified: "],
  ["当前激活", "active"],
  ["有改动尚未保存", "unsaved changes"],
  ["你即将跳转至 Gitee 进行登录授权", "You are about to sign in through Gitee"],
  ["本地有未保存的改动，读取存档会覆盖本地改动，建议您在读取存档之前，保存当前存档", "You have unsaved local changes. Loading a save will overwrite them."],
  ["您的本地存档和云文档之间有所冲突，请选择您要使用的存档", "Your local save conflicts with the cloud save. Choose which one to use."],
  ["你确定要使用本地存档吗", "Use the local save?"],
  ["你确定要使用云端存档吗", "Use the cloud save?"],
  ["未查询到该存档在服务器上的信息，请刷新后重试", "Could not find this save on the server. Refresh and try again."],
  ["新存档创建成功！", "New save created."],
  ["空荧酒馆", "KongYing Tavern"],
  ["原神地图", "Genshin Map"],
  ["点位", "Points"],
  ["地区", "Region"],
  ["地图", "Map"],
];

const translatedAttributes = ["title", "aria-label", "placeholder", "label"];
const ignoredTags = new Set(["SCRIPT", "STYLE", "TEXTAREA", "CODE", "PRE"]);

function translateText(value) {
  if (!value || !value.trim()) {
    return value;
  }

  const leading = value.match(/^\s*/u)?.[0] || "";
  const trailing = value.match(/\s*$/u)?.[0] || "";
  const text = value.trim();

  if (exactTranslations.has(text)) {
    return `${leading}${exactTranslations.get(text)}${trailing}`;
  }

  let translated = text;
  for (const [from, to] of phraseTranslations) {
    translated = translated.split(from).join(to);
  }

  return translated === text ? value : `${leading}${translated}${trailing}`;
}

function translateElement(element) {
  if (!element || ignoredTags.has(element.tagName)) {
    return;
  }

  for (const attr of translatedAttributes) {
    if (element.hasAttribute?.(attr)) {
      const next = translateText(element.getAttribute(attr));
      if (next !== element.getAttribute(attr)) {
        element.setAttribute(attr, next);
      }
    }
  }

  for (const node of element.childNodes || []) {
    if (node.nodeType === Node.TEXT_NODE) {
      const next = translateText(node.nodeValue);
      if (next !== node.nodeValue) {
        node.nodeValue = next;
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      translateElement(node);
    }
  }
}

export default boot(() => {
  document.documentElement.lang = "en";
  document.title = "Genshin Map v3";

  let translating = false;
  const translatePage = (root = document.body) => {
    if (!root || translating) {
      return;
    }
    translating = true;
    translateElement(root);
    document.title = translateText(document.title);
    translating = false;
  };

  translatePage();

  const observer = new MutationObserver((mutations) => {
    if (translating) {
      return;
    }
    for (const mutation of mutations) {
      if (mutation.type === "characterData") {
        const next = translateText(mutation.target.nodeValue);
        if (next !== mutation.target.nodeValue) {
          mutation.target.nodeValue = next;
        }
      } else if (mutation.type === "attributes") {
        translateElement(mutation.target);
      } else {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.TEXT_NODE) {
            const next = translateText(node.nodeValue);
            if (next !== node.nodeValue) {
              node.nodeValue = next;
            }
          } else if (node.nodeType === Node.ELEMENT_NODE) {
            translateElement(node);
          }
        }
      }
    }
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: translatedAttributes,
    characterData: true,
    childList: true,
    subtree: true,
  });
});
