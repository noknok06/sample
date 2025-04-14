import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  ArrowLeft,
  Building,
  Calendar,
  CheckCircle,
  Clock,
  Download,
  FileText,
  MessageSquare,
  Paperclip,
  Send,
  ThumbsUp,
  User,
  XCircle,
} from "lucide-react"

export default function RequestDetail({ params }) {
  const requestId = params.id

  // デモ用のモックデータ
  const request = {
    id: requestId,
    title: "ソフトウェアライセンスリクエスト",
    description:
      "マーケティング部門向けのAdobe Creative Cloud 25ライセンスのリクエスト。今月末までに次回のキャンペーン開始をサポートするためにこれらのライセンスが必要です。",
    company: "Acme Corp",
    requester: "Jane Smith",
    requesterRole: "マーケティングディレクター",
    status: "pending",
    priority: "high",
    createdDate: "2023-05-15",
    dueDate: "2023-05-30",
    category: "ソフトウェア",
    attachments: [
      { name: "requirements.pdf", size: "1.2 MB" },
      { name: "budget_approval.docx", size: "845 KB" },
    ],
    history: [
      { action: "リクエスト作成", user: "Jane Smith", date: "2023年5月15日", time: "09:23" },
      { action: "Acme Corpにリクエスト送信", user: "システム", date: "2023年5月15日", time: "09:24" },
      { action: "受信者によるリクエスト閲覧", user: "John Doe", date: "2023年5月16日", time: "10:15" },
    ],
    comments: [
      {
        id: 1,
        user: "John Doe",
        company: "Acme Corp",
        role: "ITマネージャー",
        content:
          "このリクエストを確認しました。どのAdobe CCアプリケーションが具体的に必要か、詳細を教えていただけますか？",
        date: "2023年5月16日",
        time: "10:30",
      },
      {
        id: 2,
        user: "Jane Smith",
        company: "あなたの会社",
        role: "マーケティングディレクター",
        content:
          "Photoshop、Illustrator、InDesign、Premiere Pro、After Effectsを含む完全なCreative Cloudスイートが必要です。",
        date: "2023年5月16日",
        time: "11:45",
      },
      {
        id: 3,
        user: "John Doe",
        company: "Acme Corp",
        role: "ITマネージャー",
        content: "ご説明ありがとうございます。完全なCreative Cloudライセンスの見積もりを準備します。",
        date: "2023年5月16日",
        time: "14:15",
      },
    ],
  }

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
        <div className="mb-6">
          <Link href="/dashboard" className="flex items-center text-blue-600 hover:text-blue-800">
            <ArrowLeft className="h-4 w-4 mr-2" />
            ダッシュボードに戻る
          </Link>
        </div>

        <div className="flex flex-col md:flex-row gap-8">
          <div className="md:w-2/3">
            <Card className="mb-8">
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center space-x-2 mb-2">
                      <StatusBadge status={request.status} />
                      <PriorityBadge priority={request.priority} />
                      <span className="text-sm text-gray-500">#{request.id}</span>
                    </div>
                    <CardTitle className="text-2xl">{request.title}</CardTitle>
                    <CardDescription className="text-sm mt-1">
                      <span className="font-medium">{request.company}</span> • {request.createdDate}に提出
                    </CardDescription>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Paperclip className="h-4 w-4 mr-2" />
                      添付
                    </Button>
                    <Button variant="outline" size="sm">
                      <FileText className="h-4 w-4 mr-2" />
                      エクスポート
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">説明</h3>
                    <p className="text-gray-900">{request.description}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-2">リクエスト者</h3>
                      <div className="flex items-center">
                        <Avatar className="h-8 w-8 mr-2">
                          <AvatarFallback>{request.requester.charAt(0)}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="text-sm font-medium">{request.requester}</p>
                          <p className="text-xs text-gray-500">{request.requesterRole}</p>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-2">カテゴリ</h3>
                      <p className="text-sm">{request.category}</p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-2">作成日</h3>
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                        <p className="text-sm">{request.createdDate}</p>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-2">期限日</h3>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-2 text-gray-400" />
                        <p className="text-sm">{request.dueDate}</p>
                      </div>
                    </div>
                  </div>

                  {request.attachments.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 mb-2">添付ファイル</h3>
                      <div className="space-y-2">
                        {request.attachments.map((attachment, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                            <div className="flex items-center">
                              <FileText className="h-4 w-4 mr-2 text-gray-400" />
                              <span className="text-sm font-medium">{attachment.name}</span>
                              <span className="text-xs text-gray-500 ml-2">({attachment.size})</span>
                            </div>
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
              <CardFooter className="border-t pt-6 flex justify-between">
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    コメント追加
                  </Button>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700 hover:bg-red-50">
                    <XCircle className="h-4 w-4 mr-2" />
                    却下
                  </Button>
                  <Button variant="outline" size="sm" className="text-amber-600 hover:text-amber-700 hover:bg-amber-50">
                    <Clock className="h-4 w-4 mr-2" />
                    保留
                  </Button>
                  <Button className="bg-green-600 hover:bg-green-700">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    承認
                  </Button>
                </div>
              </CardFooter>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>コメント</CardTitle>
                <CardDescription>リクエスト者や他の関係者とこのリクエストについて議論する</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {request.comments.map((comment) => (
                    <div key={comment.id} className="flex space-x-4">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback>{comment.user.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <p className="font-medium">{comment.user}</p>
                              <p className="text-xs text-gray-500">
                                {comment.company}の{comment.role}
                              </p>
                            </div>
                            <p className="text-xs text-gray-500">
                              {comment.date} {comment.time}
                            </p>
                          </div>
                          <p className="text-sm">{comment.content}</p>
                        </div>
                        <div className="flex items-center mt-2 text-xs text-gray-500">
                          <button className="flex items-center hover:text-blue-600">
                            <ThumbsUp className="h-3 w-3 mr-1" />
                            いいね
                          </button>
                          <span className="mx-2">•</span>
                          <button className="hover:text-blue-600">返信</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6">
                  <Textarea placeholder="コメントを追加..." className="min-h-[100px]" />
                  <div className="flex justify-between mt-2">
                    <Button variant="outline" size="sm">
                      <Paperclip className="h-4 w-4 mr-2" />
                      添付
                    </Button>
                    <Button size="sm">
                      <Send className="h-4 w-4 mr-2" />
                      送信
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="md:w-1/3">
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>リクエストステータス</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 mr-3">
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium">提出済み</p>
                      <p className="text-xs text-gray-500">2023年5月15日 09:23</p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 mr-3">
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium">受領済み</p>
                      <p className="text-xs text-gray-500">2023年5月16日 10:15</p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center text-amber-600 mr-3">
                      <Clock className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium">レビュー中</p>
                      <p className="text-xs text-gray-500">進行中</p>
                    </div>
                  </div>
                  <div className="flex items-center opacity-50">
                    <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 mr-3">
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium">承認済み</p>
                      <p className="text-xs text-gray-500">保留中</p>
                    </div>
                  </div>
                  <div className="flex items-center opacity-50">
                    <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 mr-3">
                      <CheckCircle className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium">完了</p>
                      <p className="text-xs text-gray-500">保留中</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>活動履歴</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {request.history.map((item, index) => (
                    <div key={index} className="border-l-2 border-blue-500 pl-4 py-1">
                      <p className="font-medium text-gray-900">{item.action}</p>
                      <p className="text-xs text-gray-500">{item.user}による</p>
                      <p className="text-xs text-gray-400">
                        {item.date} {item.time}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
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
