import { createRouter, createWebHistory } from "vue-router";
import List from "../views/List.vue";
import Calendar from "../views/Calendar.vue";
import Dashboard from "../views/Dashboard.vue";
import Pomodoro from "../views/Pomodoro.vue";
import Auth from "../components/Auth.vue";
import PageSettings from "../views/PageSettings.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/list" },
    { path: "/auth", component: Auth },
    { path: "/list", component: List },
    { path: "/calendar", component: Calendar },
    { path: "/dashboard", component: Dashboard },
    { path: "/pomodoro", component: Pomodoro },
    { path: "/settings", component: PageSettings },
  ],
});

// simple auth check: presence of auth token in localStorage
router.beforeEach((to) => {
  const isAuth = !!localStorage.getItem("authToken");
  const isGuest = !!localStorage.getItem("authGuest");
  const allowed = isAuth || isGuest;

  // allow guests to access the registration page explicitly
  const wantsRegister =
    to.path === "/auth" && to.query && to.query.mode === "register";

  if (to.path !== "/auth" && !allowed) {
    // redirect anonymous users to auth
    return { path: "/auth" };
  }

  if (to.path === "/auth" && allowed && !wantsRegister) {
    // authenticated/guest users should not visit auth page unless they explicitly want to register
    return { path: "/list" };
  }

  // proceed
  return undefined;
});

export default router;
