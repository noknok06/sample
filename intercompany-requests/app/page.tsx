import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, Building, CheckCircle, FileText, MessageSquare } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Building className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-semibold text-gray-900">InterConnect</h1>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/login">
              <Button variant="outline">ログイン</Button>
            </Link>
            <Link href="/register">
              <Button>登録</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        <section className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">企業間リクエストを効率化</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            企業間のリクエストを提出から承認まで、一か所で管理するためのシンプルで効率的なプラットフォームです。
          </p>
          <div className="mt-8">
            <Link href="/demo">
              <Button size="lg" className="mr-4">
                デモを見る
              </Button>
            </Link>
            <Link href="/register">
              <Button size="lg" variant="outline">
                始める
              </Button>
            </Link>
          </div>
        </section>

        <section className="grid md:grid-cols-3 gap-8 mb-16">
          <FeatureCard
            icon={<FileText className="h-8 w-8 text-blue-600" />}
            title="リクエスト管理"
            description="企業間のリクエストを簡単に提出、追跡、管理できます。"
          />
          <FeatureCard
            icon={<CheckCircle className="h-8 w-8 text-blue-600" />}
            title="承認ワークフロー"
            description="すべてのリクエストに対する合理化された確認と承認プロセス。"
          />
          <FeatureCard
            icon={<MessageSquare className="h-8 w-8 text-blue-600" />}
            title="コラボレーティブコメント"
            description="明確なコミュニケーションを確保するためのコメント機能でリクエストについて議論。"
          />
        </section>

        <section className="bg-white rounded-lg shadow-md p-8 mb-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">使い方</h3>
          <div className="grid md:grid-cols-4 gap-6">
            <WorkflowStep
              number="1"
              title="リクエスト提出"
              description="他の企業に詳細なリクエストを作成して提出します。"
            />
            <WorkflowStep number="2" title="確認" description="受信企業がリクエストの受領を確認します。" />
            <WorkflowStep
              number="3"
              title="レビューと承認"
              description="権限のある担当者によってリクエストがレビューされ承認されます。"
            />
            <WorkflowStep
              number="4"
              title="完了"
              description="リクエストが完了としてマークされ、参照用にアーカイブされます。"
            />
          </div>
        </section>

        <section className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">企業間リクエストを簡素化する準備はできましたか？</h3>
          <Link href="/register">
            <Button size="lg" className="px-8">
              今すぐ始める <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </section>
      </main>

      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-lg font-semibold mb-4">InterConnect</h4>
              <p className="text-gray-300">最新技術で企業間リクエスト管理を簡素化します。</p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">クイックリンク</h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/features" className="text-gray-300 hover:text-white">
                    機能
                  </Link>
                </li>
                <li>
                  <Link href="/pricing" className="text-gray-300 hover:text-white">
                    料金
                  </Link>
                </li>
                <li>
                  <Link href="/about" className="text-gray-300 hover:text-white">
                    会社概要
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="text-gray-300 hover:text-white">
                    お問い合わせ
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">お問い合わせ</h4>
              <p className="text-gray-300">ご質問がありますか？サポートチームにお問い合わせください。</p>
              <Link href="/contact">
                <Button variant="outline" className="mt-4 border-white text-white hover:bg-white hover:text-gray-800">
                  サポートに連絡
                </Button>
              </Link>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-300">
            <p>© {new Date().getFullYear()} InterConnect. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <Card>
      <CardHeader>
        <div className="mb-2">{icon}</div>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-base">{description}</CardDescription>
      </CardContent>
    </Card>
  )
}

function WorkflowStep({ number, title, description }) {
  return (
    <div className="flex flex-col items-center text-center">
      <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-lg mb-4">
        {number}
      </div>
      <h4 className="font-semibold text-lg mb-2">{title}</h4>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
