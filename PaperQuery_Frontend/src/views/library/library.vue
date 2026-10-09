<template>
  <div class="library-page flex-col w-full p-8">
    <div class="library-header flex items-center justify-between mb-8">
      <div>
        <p class="library-kicker">ARCHIVE / LIBRARY</p>
        <h1>你的研究资料，井然有序。</h1>
        <p class="library-description">
          按主题收集论文，在原文、笔记与对话之间保持连接。
        </p>
      </div>
      <div class="flex gap-2">
        <Button
          variant="outline"
          class="px-4 py-2"
          @click="router.push('/home/library/notes')"
          >笔记集</Button
        >
        <Button variant="outline" class="px-4 py-2" @click="toggleSelectMode">
          {{ selectMode ? '取消选择' : '批量删除' }}
        </Button>
      </div>
    </div>
    <div v-if="knowCardList" class="library-tools flex mb-6">
      <Input
        v-model="searchTerm"
        type="text"
        placeholder="搜索知识库名称或描述"
        class="w-1/2"
      />
      <Popover v-model:open="open">
        <PopoverTrigger as-child>
          <Button
            variant="outline"
            role="combobox"
            :aria-expanded="open"
            class="w-[200px] justify-between"
          >
            {{ value || '全部知识库' }}
            <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent class="w-[200px] p-0">
          <Command>
            <CommandInput class="h-9" placeholder="选择知识库" />
            <CommandEmpty>没有匹配的知识库</CommandEmpty>
            <CommandList>
              <CommandGroup>
                <CommandItem value="全部知识库" @select="resetLibraryFilter"
                  >全部知识库</CommandItem
                >
                <CommandItem
                  v-for="card in knowCardList"
                  :key="card.knowledgeName"
                  :value="card.knowledgeName"
                  @select="
                    (ev) => {
                      value = card.knowledgeName
                      open = false
                    }
                  "
                >
                  {{ card.knowledgeName }}
                  <Check
                    :class="
                      cn(
                        'ml-auto h-4 w-4',
                        value === card.knowledgeName
                          ? 'opacity-100'
                          : 'opacity-0',
                      )
                    "
                  />
                </CommandItem>
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
    <p v-if="libraryError" class="rs-empty">{{ libraryError }}</p>
    <p
      v-else-if="
        knowCardList && !filteredCardList.length && knowCardList.length
      "
      class="rs-empty"
    >
      没有匹配的知识库，尝试其他关键词。
    </p>
    <!-- 知识库卡片 -->
    <div
      v-if="knowCardList !== null"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <!-- 显示创建卡片 -->
      <Card class="library-create flex justify-center items-center w-full">
        <Dialog v-model:open="createDialogOpen">
          <DialogTrigger as-child>
            <Button variant="ghost" class="w-full h-full text-xl">
              ＋ 创建知识库
            </Button>
          </DialogTrigger>
          <div>
            <DialogContent class="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>创建知识库</DialogTitle>
              </DialogHeader>
              <div class="grid gap-4 py-4">
                <div class="grid grid-cols-4 items-center gap-4">
                  <Label for="libName" class="text-right"> 知识库名称 </Label>
                  <Input
                    id="libName"
                    v-model="newCard.knowledgeName"
                    class="col-span-3"
                    required
                    autocomplete="off"
                  />
                </div>
                <div class="grid grid-cols-4 items-center gap-4">
                  <Label for="libDes" class="text-right"> 知识库描述 </Label>
                  <Input
                    id="libDes"
                    v-model="newCard.knowledgeDescription"
                    class="col-span-3"
                    autocomplete="off"
                  />
                </div>
              </div>
              <div class="flex justify-center gap-4">
                <Button
                  variant="outline"
                  :disabled="librarySaving"
                  @click="createDialogOpen = false"
                  >取消</Button
                >
                <Button
                  :disabled="librarySaving || !newCard.knowledgeName.trim()"
                  @click="SaveEvent"
                  >{{ librarySaving ? '创建中…' : '创建知识库' }}</Button
                >
              </div>
            </DialogContent>
          </div>
        </Dialog>
      </Card>
      <Card
        v-for="card in filteredCardList"
        :key="card.knowledgeName"
        class="library-card flex-col relative"
      >
        <CardHeader>
          <CardTitle>{{ card.knowledgeName }}</CardTitle>
          <!-- 删除模式下右上角的勾选圆圈 -->
          <button
            v-if="selectMode"
            type="button"
            class="absolute top-3 right-3 h-6 w-6 rounded-full border-2 flex items-center justify-center transition-colors"
            :class="
              selectedIds.has(card.knowledgeID)
                ? 'bg-red-500 border-red-500'
                : 'bg-white border-gray-300 hover:border-gray-400'
            "
            @click.stop="toggleSelect(card.knowledgeID)"
          >
            <Check
              v-if="selectedIds.has(card.knowledgeID)"
              class="h-4 w-4 text-white"
            />
          </button>
          <!-- <CardDescription>
            <label class="text-1xl">描述</label>
          </CardDescription> -->
        </CardHeader>
        <CardContent>
          <p class="text-sm text-gray-500">
            {{
              card.knowledgeDescription ||
              '为这个知识库补充描述，让研究方向更清晰。'
            }}
          </p>
          <div class="archive-counts">
            <span>{{ card.documentNum || 0 }} 篇论文</span
            ><span>{{ card.vectorNum || 0 }} 个索引块</span>
          </div>
        </CardContent>
        <!-- 横向布局 -->
        <CardFooter>
          <div class="flex justify-left w-full">
            <!-- 点击打开按钮 跳转到 knowledge 页面 -->
            <Button
              variant="outline"
              class="text-1xl mr-2"
              @click="router_knowledge(card.knowledgeID)"
              >打开</Button
            >
            <Button
              variant="outline"
              class="text-1xl mr-2"
              @click="router_chat(card)"
              >对话</Button
            >
            <Dialog
              :open="editingLibraryId === card.knowledgeID"
              @update:open="
                (isOpen) => {
                  if (!isOpen && !librarySaving) editingLibraryId = ''
                }
              "
            >
              <DialogTrigger as-child>
                <Button
                  variant="outline"
                  class="text-1xl mr-2"
                  @click="openEditDialog(card)"
                >
                  编辑
                </Button>
              </DialogTrigger>
              <DialogContent class="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>编辑知识库</DialogTitle>
                </DialogHeader>
                <div class="grid gap-4 py-4">
                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label for="libName" class="text-right"> 知识库名称 </Label>
                    <Input
                      id="libName"
                      v-model="tempCard.knowledgeName"
                      class="col-span-3"
                    />
                  </div>
                  <div class="grid grid-cols-4 items-center gap-4">
                    <Label for="libDes" class="text-right"> 知识库描述 </Label>
                    <Input
                      id="libDes"
                      v-model="tempCard.knowledgeDescription"
                      class="col-span-3"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    :disabled="librarySaving || !tempCard.knowledgeName.trim()"
                    class="text-1xl"
                    @click="
                      EditEvent(
                        card.knowledgeID,
                        tempCard.knowledgeName,
                        tempCard.knowledgeDescription,
                      )
                    "
                  >
                    {{ librarySaving ? '保存中…' : '保存更改' }}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </CardFooter>
      </Card>
    </div>
    <div
      v-else-if="knowCardList === null"
      class="grid w-full grid-cols-3 space-x-5 h-64"
    >
      <div class="space-y-2">
        <Skeleton class="h-2/3 w-full rounded-xl" />
        <Skeleton class="h-1/8 w-2/3" />
        <Skeleton class="h-1/8 w-1/3" />
      </div>
      <div class="space-y-2">
        <Skeleton class="h-2/3 w-full rounded-xl" />
        <Skeleton class="h-1/8 w-2/3" />
        <Skeleton class="h-1/8 w-1/3" />
      </div>
      <div class="space-y-2">
        <Skeleton class="h-2/3 w-full rounded-xl" />
        <Skeleton class="h-1/8 w-2/3" />
        <Skeleton class="h-1/8 w-1/3" />
      </div>
    </div>
  </div>
  <!-- 删除模式底部操作条 -->
  <div
    v-if="selectMode"
    class="library-bulk-bar fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-4 rounded-lg border bg-white px-6 py-3 shadow-xl"
  >
    <span class="text-sm font-medium text-gray-700 mr-2">
      已选 {{ selectedIds.size }} 项
    </span>
    <Button
      variant="outline"
      class="px-4"
      @click="selectAll"
      :disabled="!knowCardList || knowCardList.length === 0"
    >
      全选
    </Button>
    <Button
      variant="outline"
      class="px-4"
      @click="cancelSelect"
      :disabled="selectedIds.size === 0"
    >
      取消已选
    </Button>
    <Button
      class="px-4 bg-red-500 hover:bg-red-600 text-white"
      @click="confirmDelete"
      :disabled="selectedIds.size === 0"
    >
      确认删除
    </Button>
  </div>
  <!-- <router-view /> -->
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import { Check, ChevronsUpDown } from 'lucide-vue-next'
import { cn } from '@/components/utils'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { useRouter } from 'vue-router'
import {
  deleteKnowledge,
  getKnowledgeList,
  createKnowledge,
  editKnowledge,
  getDocumentList,
} from '@/api/data'
import { useDocumentListStore } from '@/stores/documentList'
import {
  type Knowledge,
  type KnowledgeListResponse,
  type KnowledgeResponse,
} from '@/types/type'

import { ElMessageBox, ElNotification } from 'element-plus'

const router = useRouter()

const knowCardList = ref<Knowledge[] | null>(null)
const searchTerm = ref('')
const createDialogOpen = ref(false),
  editingLibraryId = ref(''),
  librarySaving = ref(false),
  libraryError = ref('')
const filteredCardList = computed(() =>
  (knowCardList.value || []).filter((card) => {
    const matchesSelected = !value.value || card.knowledgeName === value.value
    const needle = searchTerm.value.trim().toLowerCase()
    const matchesSearch =
      !needle ||
      `${card.knowledgeName} ${card.knowledgeDescription || ''}`
        .toLowerCase()
        .includes(needle)
    return matchesSelected && matchesSearch
  }),
)

const newCard = ref({
  knowledgeName: '',
  knowledgeDescription: '',
})

const tempCard = reactive({
  knowledgeName: '',
  knowledgeDescription: '',
})

const openEditDialog = (card: Knowledge) => {
  editingLibraryId.value = card.knowledgeID
  tempCard.knowledgeName = card.knowledgeName
  tempCard.knowledgeDescription = card.knowledgeDescription
}

onMounted(async () => {
  const router = useRouter()
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }

  try {
    const libResp = (await getKnowledgeList()) as KnowledgeListResponse
    if (libResp) {
      knowCardList.value = libResp.data.knowledgeList
    }
  } catch (error: any) {
    console.error(error.message)
    libraryError.value = '知识库暂时无法加载，请稍后刷新页面。'
    knowCardList.value = []
  }
})
const open = ref(false)
const value = ref('')
function resetLibraryFilter() {
  value.value = ''
  open.value = false
}

// 删除模式：多选状态与操作
const selectMode = ref(false)
const selectedIds = ref<Set<string>>(new Set())

// 进入/退出删除模式，退出时清空选中
const toggleSelectMode = () => {
  selectMode.value = !selectMode.value
  selectedIds.value = new Set()
}

// 勾选/取消勾选单个知识
const toggleSelect = (knowledgeID: string) => {
  const next = new Set(selectedIds.value)
  if (next.has(knowledgeID)) next.delete(knowledgeID)
  else next.add(knowledgeID)
  selectedIds.value = next
}

// 全选当前列表
const selectAll = () => {
  selectedIds.value = new Set(
    (knowCardList.value ?? []).map((c) => c.knowledgeID),
  )
}

// 取消所有已选
const cancelSelect = () => {
  selectedIds.value = new Set()
}

// 确认删除选中知识
const confirmDelete = async () => {
  const ids = [...selectedIds.value]
  if (ids.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确认删除选中的 ${ids.length} 个知识库？其下全部文档、向量与源文件将一并删除，且不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }
  try {
    await deleteKnowledge(ids)
    // 从列表中移除已删除的知识
    knowCardList.value = (knowCardList.value ?? []).filter(
      (c) => !selectedIds.value.has(c.knowledgeID),
    )
    ElNotification.success(`已删除 ${ids.length} 个知识库`)
  } catch (error: any) {
    ElNotification.error(error.message || '删除失败')
  } finally {
    selectedIds.value = new Set()
    selectMode.value = false
  }
}

const router_knowledge = (knowledgeID: string) => {
  router.push({ name: 'knowledge', params: { knowledgeID: knowledgeID } })
}

// 点击「对话」：把该知识库内已处理完成的文档绑定到 Chat 的多文件对话，并跳转
const router_chat = async (card: Knowledge) => {
  try {
    const resp = (await getDocumentList(card.knowledgeID)) as any
    const docs = resp?.data || []
    const store = useDocumentListStore()
    let bound = 0
    docs.forEach((doc: any) => {
      // 只有处理完成(状态 2)的文档才有向量，能被 RAG 检索
      if (doc.documentStatus === 2) {
        store.appendDocument({
          isLoading: false,
          documentID: doc.documentID,
          documentName: doc.documentName,
          knowledgeID: card.knowledgeID,
          source: 'library',
        })
        bound += 1
      }
    })
    if (bound === 0) {
      ElNotification.warning({
        title: '暂无可用文档',
        message: '该知识库还没有处理完成的文档，无法进行对话',
      })
      return
    }
    router.push('/home/Chat')
  } catch (error: any) {
    ElNotification.error({
      title: '错误',
      message: error.message || '获取文档列表失败',
    })
  }
}

// 保存新创建的知识卡片
const SaveEvent = async () => {
  if (librarySaving.value) return
  const knowledgeName = newCard.value.knowledgeName.trim()
  const knowledgeDescription = newCard.value.knowledgeDescription.trim()
  if (!knowledgeName) return ElNotification.error('知识库名称不能为空')
  librarySaving.value = true
  try {
    const knowResp = (await createKnowledge(
      knowledgeName,
      knowledgeDescription,
    )) as KnowledgeResponse
    if (knowResp.status_code !== 200)
      throw new Error(knowResp.msg || '创建失败')
    if (!knowCardList.value) knowCardList.value = []
    knowCardList.value.unshift(knowResp.data)
    newCard.value.knowledgeName = ''
    newCard.value.knowledgeDescription = ''
    createDialogOpen.value = false
    ElNotification.success('创建知识库成功')
  } catch (error: any) {
    ElNotification.error(
      error?.response?.data?.detail || error.message || '创建失败，请重试',
    )
  } finally {
    librarySaving.value = false
  }
}

// 编辑知识卡片
// TODO: 编辑知识卡片
const EditEvent = async (
  knowledgeID: string,
  knowledgeName: string,
  knowledgeDescription: string,
) => {
  if (librarySaving.value) return
  if (!knowledgeName.trim()) return ElNotification.error('知识库名称不能为空')
  librarySaving.value = true
  try {
    const response = (await editKnowledge(
      knowledgeID,
      knowledgeName.trim(),
      knowledgeDescription,
    )) as KnowledgeResponse
    if (response.status_code !== 200)
      throw new Error(response.msg || '保存失败')
    const index = knowCardList.value?.findIndex(
      (card) => card.knowledgeID === knowledgeID,
    )
    if (index !== undefined && index !== -1)
      knowCardList.value?.splice(index, 1, response.data)
    editingLibraryId.value = ''
    ElNotification.success('编辑知识库成功')
  } catch (error: any) {
    ElNotification.error(
      error?.response?.data?.detail || error.message || '保存失败，请重试',
    )
  } finally {
    librarySaving.value = false
  }
}
</script>

<style scoped>
/* 添加所需的自定义样式 */
.archive-counts {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--rs-muted);
  margin-top: 18px;
}
.library-bulk-bar {
  max-width: calc(100vw - 24px);
  width: max-content;
  flex-wrap: wrap;
  justify-content: center;
  border-radius: 12px;
  padding: 12px 18px;
  background: #fff;
  box-shadow: 0 12px 40px #20212418;
}
@media (max-width: 600px) {
  .library-bulk-bar {
    bottom: 14px;
    gap: 8px;
    padding: 10px;
    left: 50%;
    font-size: 11px;
  }
  .library-bulk-bar > span {
    width: 100%;
    text-align: center;
  }
  .library-bulk-bar button {
    font-size: 11px;
  }
}
</style>
