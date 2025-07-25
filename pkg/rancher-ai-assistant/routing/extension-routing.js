// definition of a "blank cluster" in Rancher Dashboard
import ListResource from '@shell/pages/c/_cluster/_product/_resource/index.vue';
import CreateResource from '@shell/pages/c/_cluster/_product/_resource/create.vue';
import ViewResource from '@shell/pages/c/_cluster/_product/_resource/_id.vue';
import ViewNamespacedResource from '@shell/pages/c/_cluster/_product/_resource/_namespace/_id.vue';
import ChatBotPage from '../pages/chatBotPage.vue';
import ConfigurationPage from '../pages/configurationPage.vue';
import RancherBotOWUI from '../pages/rancherBotOWUI.vue';
import Chat from '../pages/simpleChat.vue';
const BLANK_CLUSTER = '_';
// to achieve naming consistency throughout the extension
// we recommend this to be defined on a config file and exported
// so that the developer can import it wherever it needs to be used
const YOUR_PRODUCT_NAME = 'rancher-ai-assistant';
const CUSTOM_PAGE_NAME = 'RancherBot';
const CUSTOM_PAGE_OWUI = 'RancherBotOWUI';
const CUSTOM_PAGE_SCHAT = 'Chat';
const CUSTOM_PAGE_CONFIG = 'Config';
const routes = [
  // this covers the "custom page"
  {
    name:      `${ YOUR_PRODUCT_NAME }-c-cluster-${ CUSTOM_PAGE_NAME }`,
    path:      `/${ YOUR_PRODUCT_NAME }/c/:cluster/${ CUSTOM_PAGE_NAME }`,
    component: ChatBotPage,
    meta:      {
      product: YOUR_PRODUCT_NAME,
      cluster: BLANK_CLUSTER
    },
  },
  {
    name:      `${ YOUR_PRODUCT_NAME }-c-cluster-${ CUSTOM_PAGE_CONFIG }`,
    path:      `/${ YOUR_PRODUCT_NAME }/c/:cluster/${ CUSTOM_PAGE_CONFIG }`,
    component: ConfigurationPage,
    meta:      {
      product: YOUR_PRODUCT_NAME,
      cluster: BLANK_CLUSTER
    },
  },
  {
    name:      `${ YOUR_PRODUCT_NAME }-c-cluster-${ CUSTOM_PAGE_OWUI }`,
    path:      `/${ YOUR_PRODUCT_NAME }/c/:cluster/${ CUSTOM_PAGE_OWUI }`,
    component: RancherBotOWUI,
    meta:      {
      product: YOUR_PRODUCT_NAME,
      cluster: BLANK_CLUSTER
    },
  },
  {
    name:      `${ YOUR_PRODUCT_NAME }-c-cluster-${ CUSTOM_PAGE_SCHAT }`,
    path:      `/${ YOUR_PRODUCT_NAME }/c/:cluster/${ CUSTOM_PAGE_SCHAT }`,
    component: Chat,
    meta:      {
      product: YOUR_PRODUCT_NAME,
      cluster: BLANK_CLUSTER
    },
  },
  // the following routes cover the "resource page"
  // registering routes for list/edit/create views
  {
    name:      `${ YOUR_PRODUCT_NAME }-c-cluster-resource`,
    path:      `/${ YOUR_PRODUCT_NAME }/c/:cluster/:resource`,
    component: ListResource,
    meta:      {
      product: YOUR_PRODUCT_NAME,
      cluster: BLANK_CLUSTER
    },
  },
  {
    name:      `${ YOUR_PRODUCT_NAME }-c-cluster-resource-create`,
    path:      `/${ YOUR_PRODUCT_NAME }/c/:cluster/:resource/create`,
    component: CreateResource,
    meta:      {
      product: YOUR_PRODUCT_NAME,
      cluster: BLANK_CLUSTER
    },
  },
  {
    name:      `${ YOUR_PRODUCT_NAME }-c-cluster-resource-id`,
    path:      `/${ YOUR_PRODUCT_NAME }/c/:cluster/:resource/:id`,
    component: ViewResource,
    meta:      {
      product: YOUR_PRODUCT_NAME,
      cluster: BLANK_CLUSTER
    },
  },
  {
    name:      `${ YOUR_PRODUCT_NAME }-c-cluster-resource-namespace-id`,
    path:      `/${ YOUR_PRODUCT_NAME }/:cluster/:resource/:namespace/:id`,
    component: ViewNamespacedResource,
    meta:      {
      product: YOUR_PRODUCT_NAME,
      cluster: BLANK_CLUSTER
    },
  }
];

export default routes;
