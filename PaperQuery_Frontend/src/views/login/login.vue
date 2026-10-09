<script setup lang="ts">
import {
  ArrowRight,
  Eye,
  EyeOff,
  FileSearch2,
  ListChecks,
  LockKeyhole,
  MessagesSquare,
  UserRound,
} from 'lucide-vue-next'
import { ElNotification } from 'element-plus'
import { login, register } from '@/api/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import LoginCosmosVisual from './LoginCosmosVisual.vue'

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const teamName = ref('')
const registering = ref(false)
const showPassword = ref(false)
const busy = ref(false)
const authMessage = ref('')
const authFailed = ref(false)
const ambientPaused = ref(false)
const router = useRouter()
const url = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001'

const features = [
  {
    title: '证据可溯源',
    description: '据实引用，来源可查',
    icon: FileSearch2,
    variant: 'evidence',
  },
  {
    title: '混合检索问答',
    description: '融合多源，获得更准答案',
    icon: MessagesSquare,
    variant: 'answers',
  },
  {
    title: '科研任务编排',
    description: '计划有序，高效推进',
    icon: ListChecks,
    variant: 'tasks',
  },
]

function switchMode() {
  if (busy.value) return
  registering.value = !registering.value
  confirmPassword.value = ''
  showPassword.value = false
  authMessage.value = ''
}

async function submitAuth() {
  if (busy.value) return
  if (registering.value && password.value !== confirmPassword.value) {
    authFailed.value = true
    authMessage.value = '两次输入的密码不一致，请重新确认。'
    ElNotification.error({ title: '注册失败', message: '两次输入的密码不一致' })
    return
  }

  busy.value = true
  authMessage.value = ''
  authFailed.value = false
  try {
    if (registering.value) {
      const res = await register(url, {
        username: username.value,
        password: password.value,
        teamName: teamName.value,
      })
      registering.value = false
      confirmPassword.value = ''
      authMessage.value = '账户已创建，请使用新账户登录。'
      ElNotification.success({
        title: '注册成功',
        message: res?.msg || '请使用新账户登录',
      })
      return
    }

    await login(url, { username: username.value, password: password.value })
    ElNotification({
      title: '登录成功',
      type: 'success',
      customClass: 'login-notify-fade-up',
    })
    await router.push('/home')
  } catch (error) {
    authFailed.value = true
    authMessage.value = error instanceof Error ? error.message : '暂时无法连接，请稍后重试。'
    ElNotification({
      title: registering.value ? '注册失败' : '登录失败',
      type: 'error',
      message: error instanceof Error ? error.message : '发生未知错误',
      customClass: 'login-notify-fade-up',
    })
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <main id="home" class="rs-page">
    <LoginCosmosVisual :paused="ambientPaused" />
    <div class="rs-page-inner">
      <header class="rs-header">
        <a class="rs-brand" href="#home" aria-label="研境 ResearchSpace 首页">
          <span class="rs-brand-mark"
            ><img src="/brand/researchspace-dark.svg" alt=""
          /></span>
          <span>ResearchSpace<span class="rs-brand-cn">研境 · 智能研究工作台</span></span>
        </a>
        <nav class="rs-nav" aria-label="页面导航">
          <a class="rs-nav-active" href="#home" aria-current="page">首页</a>
          <a href="#features">功能</a>
          <a href="#about">关于</a>
        </nav>
        <button class="rs-motion-toggle" type="button" :aria-pressed="ambientPaused" @click="ambientPaused = !ambientPaused">{{ ambientPaused ? '继续环境动效' : '暂停环境动效' }}</button>
      </header>

      <div class="rs-main-row" :class="{ 'rs-registering': registering }">
        <section id="about" class="rs-hero" aria-labelledby="rs-hero-title">
          <div class="rs-hero-copy">
            <p class="rs-hero-eyebrow">BEYOND THE KNOWN</p>
            <h1 id="rs-hero-title" class="rs-hero-title">
              <span>向未知，</span>
              <span>再进一步。</span>
            </h1>
            <h2>每一次阅读，都是发现的开始。</h2>
            <p>连接论文、证据与灵感。<br />让值得探索的问题，抵达可信的答案。</p>
            <div class="rs-hero-coordinate" aria-hidden="true"><span class="rs-coordinate-line" /> TIME · EVIDENCE · DISCOVERY</div>
          </div>
        </section>

        <section class="rs-auth-card" aria-labelledby="rs-auth-title">
          <div class="rs-auth-content">
            <div class="rs-auth-heading">
              <span class="rs-auth-kicker">YOUR RESEARCH STARTS HERE</span>
              <h2 id="rs-auth-title">
                {{ registering ? '创建账户' : '欢迎回来' }}
              </h2>
              <p>
                {{
                  registering
                    ? '注册研境 ResearchSpace'
                    : '登录研境 ResearchSpace'
                }}
              </p>
            </div>

            <form class="rs-auth-form" @submit.prevent="submitAuth">
              <div class="rs-field">
                <Label for="username" class="rs-field-label">用户名</Label>
                <UserRound :size="22" :stroke-width="1.8" aria-hidden="true" />
                <Input
                  id="username"
                  v-model="username"
                  placeholder="用户名"
                  autocomplete="username"
                  required
                  :disabled="busy"
                />
              </div>
              <div class="rs-field">
                <Label for="password" class="rs-field-label">密码</Label>
                <LockKeyhole
                  :size="22"
                  :stroke-width="1.8"
                  aria-hidden="true"
                />
                <Input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="密码"
                  :autocomplete="
                    registering ? 'new-password' : 'current-password'
                  "
                  :minlength="registering ? 8 : undefined"
                  required
                  :disabled="busy"
                />
                <button
                  class="rs-password-toggle"
                  type="button"
                  :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                  :aria-pressed="showPassword"
                  :disabled="busy"
                  @click="showPassword = !showPassword"
                >
                  <EyeOff v-if="showPassword" :size="21" aria-hidden="true" />
                  <Eye v-else :size="21" aria-hidden="true" />
                </button>
              </div>

              <template v-if="registering">
                <div class="rs-field">
                  <Label for="confirm-password" class="rs-field-label"
                    >确认密码</Label
                  >
                  <LockKeyhole
                    :size="22"
                    :stroke-width="1.8"
                    aria-hidden="true"
                  />
                  <Input
                    id="confirm-password"
                    v-model="confirmPassword"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="确认密码"
                    autocomplete="new-password"
                    required
                    :disabled="busy"
                  />
                </div>
                <div class="rs-field">
                  <Label for="team-name" class="rs-field-label"
                    >团队名（可选）</Label
                  >
                  <MessagesSquare
                    :size="22"
                    :stroke-width="1.8"
                    aria-hidden="true"
                  />
                  <Input
                    id="team-name"
                    v-model="teamName"
                    placeholder="团队名（可选）"
                    autocomplete="off"
                    :disabled="busy"
                  />
                </div>
                <p class="rs-team-hint">
                  填写团队名后将提交加入申请，待管理员审批。
                </p>
              </template>

              <Button
                class="rs-submit"
                type="submit"
                :disabled="busy"
                :aria-busy="busy"
              >
                <span>{{
                  busy ? (registering ? '正在创建账户…' : '正在进入工作台…') : registering ? '创建研究账户' : '进入研究空间'
                }}</span>
                <ArrowRight
                  v-if="!busy"
                  :size="21"
                  :stroke-width="1.8"
                  aria-hidden="true"
                />
              </Button>
              <p v-if="authMessage" class="rs-auth-message" :class="{ 'is-error': authFailed }" role="status" aria-live="polite">{{ authMessage }}</p>
            </form>
          </div>

          <div class="rs-auth-switch">
            <span>{{ registering ? '已有账户？' : '没有账号？' }}</span>
            <button type="button" :disabled="busy" @click="switchMode">
              {{ registering ? '返回登录' : '立即注册' }}
            </button>
          </div>
        </section>
      </div>

      <section id="features" class="rs-features" aria-label="平台功能">
        <article
          v-for="feature in features"
          :key="feature.variant"
          class="rs-feature"
          :class="`rs-feature-${feature.variant}`"
        >
          <div class="rs-feature-icon">
            <component
              :is="feature.icon"
              :size="29"
              :stroke-width="1.8"
              aria-hidden="true"
            />
          </div>
          <div class="rs-feature-copy">
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
          <div class="rs-feature-art" aria-hidden="true">
            <template v-if="feature.variant === 'evidence'">
              <span class="rs-art-sheet rs-art-sheet-back" /><span
                class="rs-art-sheet rs-art-sheet-front"
              /><span class="rs-art-lens" />
            </template>
            <template v-else-if="feature.variant === 'answers'">
              <span class="rs-art-answer-sheet" /><span class="rs-art-bubble"
                ><i /><i /><i
              /></span>
            </template>
            <template v-else
              ><span class="rs-art-task-list"><i /><i /><i /></span
            ></template>
          </div>
        </article>
      </section>
    </div>
  </main>
</template>

<style scoped src="./login.css"></style>

<style>
#app:has(.rs-page) {
  height: auto;
  min-height: 100vh;
  overflow: visible;
}
#app:has(.rs-page) > div {
  height: auto;
  width: 100%;
}
.login-notify-fade-up {
  animation: rs-notification-in 240ms ease-out both;
}
@keyframes rs-notification-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@media (prefers-reduced-motion: reduce) {
  .login-notify-fade-up {
    animation: none;
  }
}
</style>
