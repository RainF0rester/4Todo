import { createRouter, createWebHistory } from "vue-router";
import { Modal } from "ant-design-vue";
import List from "../views/List.vue";
import Calendar from "../views/Calendar.vue";
import Dashboard from "../views/Dashboard.vue";
import Pomodoro from "../views/Pomodoro.vue";
import Auth from "../components/Auth.vue";
import Home from "../views/Home.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/list" },
    { path: "/home", component: Home },
    { path: "/auth", component: Auth },
    { path: "/list", component: List },
    { path: "/calendar", component: Calendar },
    { path: "/dashboard", component: Dashboard },
    { path: "/pomodoro", component: Pomodoro },

  ],
});

// simple auth check: presence of auth token in localStorage
router.beforeEach((to) => {
  const isAuth = !!localStorage.getItem("authToken");
  const isGuest = !!localStorage.getItem("authGuest");
  const allowed = isAuth || isGuest;

  // allow guests to access the registration page explicitly
  const wantsRegister =
    to.path === "/auth" && to.query && to.query.mode === "login";

  let guestModalOpen = false;
  if (to.path !== "/auth" && !allowed) {
    // redirect anonymous users to auth
    return { path: "/auth" };
  }

  // if the user is a guest and tries to access other pages, show a modal and redirect to auth
    if (isGuest && !isAuth) {
    const guestOk = (to.path === "/list") || (to.path === "/auth") || (to.path === "/home")
    if (!guestOk) {
      if (!guestModalOpen) {
        guestModalOpen =  true;
        Modal.confirm({
          title: "Guest Access Restricted",
          content:
            "Unable to access this page for guests. Please login or register to save your data.",
          okText: "login",
          cancelText: "cancel",
          centered: true,
          onOk() {
            localStorage.removeItem("authGuest");
            return router.push({ path: "/auth" });
          },
          onCancel() {
            router.replace("/list");
          },
          afterClose() {
            guestModalOpen = false;
          },
        });
      }
      return false;
    }
  }
  
  if (to.path === "/auth" && allowed && !wantsRegister) {
    // authenticated/guest users should not visit auth page unless they explicitly want to register
    if (isAuth) {
      return { path: "/home" };
    }
  }

  // proceed
  return undefined;
});

export default router;
