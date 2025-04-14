import { Textarea } from "@/components/ui/textarea"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ArrowLeft, Building, Plus, Search, Users } from "lucide-react"

export default function CompaniesPage() {
  // デモ用のモックデータ
  const companies = [
    {
      id: 1,
      name: "Acme Corp",
      industry: "テクノロジー",
      contacts: 5,
      activeRequests: 3,
      status: "active",
      lastActivity: "2時間前",
    },
    {
      id: 2,
      name: "TechGiant Inc",
      industry: "ソフトウェア",
      contacts: 3,
      activeRequests: 2,
      status: "active",
      lastActivity: "1日前",
    },
    {
      id: 3,
      name: "Innovate LLC",
      industry: "コンサルティング",
      contacts: 2,
      activeRequests: 1,
      status: "active",
      lastActivity: "3日前",
    },
    {
      id: 4,
      name: "DataFlow Systems",
      industry: "データサービス",
      contacts: 4,
      activeRequests: 0,
      status: "active",
      lastActivity: "1週間前",
    },
    {
      id: 5,
      name: "SaaS Solutions",
      industry: "ソフトウェア",
      contacts: 2,
      activeRequests: 1,
      status: "active",
      lastActivity: "2日前",
    },
    {
      id: 6,
      name: "DevOps Pro",
      industry: "ITサービス",
      contacts: 1,
      activeRequests: 0,
      status: "inactive",
      lastActivity: "1ヶ月前",
    },
    {
      id: 7,
      name: "BrandBoost",
      industry: "マーケティング",
      contacts: 3,
      activeRequests: 0,
      status: "active",
      lastActivity: "2週間前",
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
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/dashboard" className="flex items-center text-blue-600 hover:text-blue-800">
            <ArrowLeft className="h-4 w-4 mr-2" />
            ダッシュボードに戻る
          </Link>
        </div>

        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">企業管理</h2>
          <Link href="/dashboard/companies/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              企業を追加
            </Button>
          </Link>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>接続企業</CardTitle>
            <CardDescription>他の企業との接続を管理する</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between mb-6">
              <div className="relative w-64">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input placeholder="企業を検索..." className="pl-10" />
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  アクティブ
                </Button>
                <Button variant="outline" size="sm">
                  非アクティブ
                </Button>
                <Button variant="outline" size="sm">
                  すべて
                </Button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">企業</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">業種</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">連絡先</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">アクティブなリクエスト</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">ステータス</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">最終アクティビティ</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">アクション</th>
                  </tr>
                </thead>
                <tbody>
                  {companies.map((company) => (
                    <tr key={company.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-4">
                        <div className="flex items-center">
                          <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium mr-3">
                            {company.name.charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{company.name}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-500">{company.industry}</td>
                      <td className="px-4 py-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <Users className="h-4 w-4 mr-2 text-gray-400" />
                          {company.contacts}
                        </div>
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-500">{company.activeRequests}</td>
                      <td className="px-4 py-4 text-sm">
                        <StatusBadge status={company.status} />
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-500">{company.lastActivity}</td>
                      <td className="px-4 py-4 text-sm">
                        <div className="flex space-x-2">
                          <Link href={`/dashboard/companies/${company.id}`}>
                            <Button variant="outline" size="sm">
                              表示
                            </Button>
                          </Link>
                          <Button variant="outline" size="sm">
                            編集
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>企業招待</CardTitle>
            <CardDescription>新しい企業を招待して組織と接続する</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="company-email">企業メール</Label>
                <Input id="company-email" placeholder="企業のメールアドレスを入力" />
              </div>
              <div>
                <Label htmlFor="message">招待メッセージ</Label>
                <Textarea id="message" placeholder="招待状に個人的なメッセージを追加" className="min-h-[100px]" />
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              招待を送信
            </Button>
          </CardFooter>
        </Card>
      </main>
    </div>
  )
}

function Label({ htmlFor, children }) {
  return (
    <label htmlFor={htmlFor} className="block text-sm font-medium text-gray-700 mb-1">
      {children}
    </label>
  )
}

function StatusBadge({ status }) {
  const statusStyles = {
    active: "bg-green-100 text-green-800",
    inactive: "bg-gray-100 text-gray-800",
    pending: "bg-amber-100 text-amber-800",
  }

  const statusText = {
    active: "アクティブ",
    inactive: "非アクティブ",
    pending: "保留中",
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusStyles[status]}`}>{statusText[status]}</span>
  )
}
