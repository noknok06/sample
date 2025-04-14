import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Building, Clock, FileText, Filter, Plus, Search, Settings, User } from "lucide-react"

export default function Dashboard() {
  // デモ用のモックデータ
  const pendingRequests = [
    {
      id: 1,
      title: "ソフトウェアライセンスリクエスト",
      company: "Acme Corp",
      status: "pending",
      date: "2023-05-15",
      priority: "high",
    },
    {
      id: 2,
      title: "マーケティング協力",
      company: "TechGiant Inc",
      status: "pending",
      date: "2023-05-14",
      priority: "medium",
    },
    {
      id: 3,
      title: "合弁事業提案",
      company: "Innovate LLC",
      status: "pending",
      date: "2023-05-12",
      priority: "low",
    },
  ]

  const approvedRequests = [
    {
      id: 4,
      title: "データ共有契約",
      company: "DataFlow Systems",
      status: "approved",
      date: "2023-05-10",
      priority: "high",
    },
    {
      id: 5,
      title: "製品統合",
      company: "SaaS Solutions",
      status: "approved",
      date: "2023-05-08",
      priority: "medium",
    },
  ]

  const completedRequests = [
    {
      id: 6,
      title: "APIアクセスリクエスト",
      company: "DevOps Pro",
      status: "completed",
      date: "2023-05-05",
      priority: "medium",
    },
    {
      id: 7,
      title: "共同マーケティングキャンペーン",
      company: "BrandBoost",
      status: "completed",
      date: "2023-05-01",
      priority: "high",
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Building className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-semibold text-gray-900">InterConnect</h1>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm">
              <Settings className="h-5 w-5 mr-2" />
              設定
            </Button>
            <Button variant="ghost" size="sm">
              <User className="h-5 w-5 mr-2" />
              プロフィール
            </Button>
            <Link href="/login">
              <Button variant="outline" size="sm">
                ログアウト
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">ダッシュボード</h2>
          <Link href="/dashboard/requests/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新規リクエスト
            </Button>
          </Link>
        </div>

        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <StatCard title="リクエスト総数" value="42" icon={<FileText className="h-8 w-8 text-blue-600" />} />
          <StatCard title="承認待ち" value="12" icon={<Clock className="h-8 w-8 text-amber-500" />} />
          <StatCard title="承認済み" value="18" icon={<Badge className="h-8 w-8 text-green-500" />} />
          <StatCard title="接続企業数" value="8" icon={<Building className="h-8 w-8 text-purple-500" />} />
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold text-gray-900">リクエスト管理</h3>
            <div className="flex space-x-2">
              <div className="relative">
                <Search className="h-4 w-4 absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="リクエストを検索..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <Tabs defaultValue="pending">
            <TabsList className="mb-6">
              <TabsTrigger value="pending">保留中</TabsTrigger>
              <TabsTrigger value="approved">承認済み</TabsTrigger>
              <TabsTrigger value="completed">完了</TabsTrigger>
              <TabsTrigger value="all">すべて</TabsTrigger>
            </TabsList>

            <TabsContent value="pending">
              <RequestTable requests={pendingRequests} />
            </TabsContent>

            <TabsContent value="approved">
              <RequestTable requests={approvedRequests} />
            </TabsContent>

            <TabsContent value="completed">
              <RequestTable requests={completedRequests} />
            </TabsContent>

            <TabsContent value="all">
              <RequestTable requests={[...pendingRequests, ...approvedRequests, ...completedRequests]} />
            </TabsContent>
          </Tabs>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>最近のアクティビティ</CardTitle>
              <CardDescription>リクエストに関する最新のアクション</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <ActivityItem
                  title="マーケティング協力が承認されました"
                  description="TechGiant Incがリクエストを承認しました"
                  time="2時間前"
                />
                <ActivityItem
                  title="ソフトウェアライセンスリクエストに新しいコメント"
                  description="Acme CorpのJohn：「詳細が必要です」"
                  time="5時間前"
                />
                <ActivityItem
                  title="合弁事業提案が提出されました"
                  description="Innovate LLCに新しいリクエストを提出しました"
                  time="1日前"
                />
                <ActivityItem
                  title="データ共有契約が完了しました"
                  description="すべての関係者が要件を満たしました"
                  time="3日前"
                />
              </div>
            </CardContent>
            <CardFooter>
              <Link href="/dashboard/activity">
                <Button variant="outline" size="sm">
                  すべてのアクティビティを表示
                </Button>
              </Link>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>企業接続</CardTitle>
              <CardDescription>接続している企業</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <CompanyItem name="Acme Corp" activeRequests={3} />
                <CompanyItem name="TechGiant Inc" activeRequests={2} />
                <CompanyItem name="Innovate LLC" activeRequests={1} />
                <CompanyItem name="DataFlow Systems" activeRequests={0} />
                <CompanyItem name="SaaS Solutions" activeRequests={1} />
              </div>
            </CardContent>
            <CardFooter>
              <Link href="/dashboard/companies">
                <Button variant="outline" size="sm">
                  企業を管理
                </Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
      </main>
    </div>
  )
}

function StatCard({ title, value, icon }) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-3xl font-bold mt-2">{value}</p>
          </div>
          <div>{icon}</div>
        </div>
      </CardContent>
    </Card>
  )
}

function RequestTable({ requests }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">ID</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">タイトル</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">企業</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">ステータス</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">日付</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">優先度</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">アクション</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((request) => (
            <tr key={request.id} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="px-4 py-4 text-sm text-gray-500">#{request.id}</td>
              <td className="px-4 py-4 text-sm font-medium text-gray-900">{request.title}</td>
              <td className="px-4 py-4 text-sm text-gray-500">{request.company}</td>
              <td className="px-4 py-4 text-sm">
                <StatusBadge status={request.status} />
              </td>
              <td className="px-4 py-4 text-sm text-gray-500">{request.date}</td>
              <td className="px-4 py-4 text-sm">
                <PriorityBadge priority={request.priority} />
              </td>
              <td className="px-4 py-4 text-sm">
                <Link href={`/dashboard/requests/${request.id}`}>
                  <Button variant="outline" size="sm">
                    表示
                  </Button>
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function StatusBadge({ status }) {
  const statusStyles = {
    pending: "bg-amber-100 text-amber-800",
    approved: "bg-green-100 text-green-800",
    completed: "bg-blue-100 text-blue-800",
    rejected: "bg-red-100 text-red-800",
  }

  const statusText = {
    pending: "保留中",
    approved: "承認済み",
    completed: "完了",
    rejected: "却下",
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusStyles[status]}`}>{statusText[status]}</span>
  )
}

function PriorityBadge({ priority }) {
  const priorityStyles = {
    high: "bg-red-100 text-red-800",
    medium: "bg-blue-100 text-blue-800",
    low: "bg-gray-100 text-gray-800",
  }

  const priorityText = {
    high: "高",
    medium: "中",
    low: "低",
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${priorityStyles[priority]}`}>
      {priorityText[priority]}
    </span>
  )
}

function ActivityItem({ title, description, time }) {
  return (
    <div className="border-l-2 border-blue-500 pl-4 py-1">
      <p className="font-medium text-gray-900">{title}</p>
      <p className="text-sm text-gray-600">{description}</p>
      <p className="text-xs text-gray-400 mt-1">{time}</p>
    </div>
  )
}

function CompanyItem({ name, activeRequests }) {
  return (
    <div className="flex justify-between items-center">
      <div className="flex items-center">
        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium">
          {name.charAt(0)}
        </div>
        <div className="ml-3">
          <p className="font-medium text-gray-900">{name}</p>
          <p className="text-xs text-gray-500">{activeRequests} 件のアクティブなリクエスト</p>
        </div>
      </div>
      <Link href={`/dashboard/companies/${name.toLowerCase().replace(/\s+/g, "-")}`}>
        <Button variant="ghost" size="sm">
          表示
        </Button>
      </Link>
    </div>
  )
}
