/**
 * Vue Router. All routes are managed here.
 */
import Vue from 'vue'
import VueRouter from 'vue-router'

// Use lazy loading to improve page size
const Home = () => import('../views/Home')
const QA = () => import('../views/QA')
const Explain = () => import('../views/Explain')
const Skills = () => import('../views/Skills')
const Skill = () => import('../views/Skill')
const Feedback = () => import('../views/Feedback')
const Terms = () => import('../views/Terms')
const Privacy = () => import('../views/Privacy')
const SignIn = () => import('../views/SignIn')
const NotFound = () => import('../views/NotFound')

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/qa',
    name: 'qa',
    component: QA
  },
  {
    path: '/skills',
    name: 'skills',
    component: Skills,
    meta: {
      requiresAuthentication: true
    }
  },
  {
    path: '/skills/:id',
    name: 'skill',
    component: Skill,
    meta: {
      requiresAuthentication: true
    }
  },
  {
    path: '/explain',
    name: 'explain',
    component: Explain
  },
  {
    path: '/feedback',
    name: 'feedback',
    component: Feedback
  },
  {
    path: '/terms-and-conditions',
    name: 'terms',
    component: Terms
  },
  {
    path: '/privacy-policy',
    name: 'privacy',
    component: Privacy
  },
  {
    path: '/signin',
    name: 'signIn',
    component: SignIn
  },
  {
    path: '*',
    name: 'notfound',
    component: NotFound
  }
]

const router = new VueRouter({
  routes,
  mode: 'history',
  scrollBehavior (to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  }
})

export default router
