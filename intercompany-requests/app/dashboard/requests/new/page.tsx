import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { ArrowLeft, Building, Paperclip, Send } from "lucide-react"

export default function NewRequest() {
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

        <div className="max-w-3xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>新規リクエスト</CardTitle>
              <CardDescription>他の企業に送信する新しいリクエストを作成する</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="recipient-company">受信企業</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="企業を選択" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="acme">Acme Corp</SelectItem>
                        <SelectItem value="techgiant">TechGiant Inc</SelectItem>
                        <SelectItem value="innovate">Innovate LLC</SelectItem>
                        <SelectItem value="dataflow">DataFlow Systems</SelectItem>
                        <SelectItem value="saas">SaaS Solutions</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="title">リクエストタイトル</Label>
                    <Input id="title" placeholder="リクエストの明確なタイトルを入力してください" />
                  </div>

                  <div>
                    <Label htmlFor="category">カテゴリ</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="カテゴリを選択" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="software">ソフトウェア</SelectItem>
                        <SelectItem value="hardware">ハードウェア</SelectItem>
                        <SelectItem value="services">サービス</SelectItem>
                        <SelectItem value="partnership">パートナーシップ</SelectItem>
                        <SelectItem value="data">データ共有</SelectItem>
                        <SelectItem value="other">その他</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="description">説明</Label>
                    <Textarea
                      id="description"
                      placeholder="リクエストの詳細な説明を提供してください"
                      className="min-h-[150px]"
                    />
                  </div>

                  <div>
                    <Label htmlFor="due-date">期限日（任意）</Label>
                    <Input id="due-date" type="date" />
                  </div>

                  <div>
                    <Label>優先度</Label>
                    <RadioGroup defaultValue="medium" className="flex space-x-4 mt-2">
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="low" id="low" />
                        <Label htmlFor="low" className="cursor-pointer">
                          低
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="medium" id="medium" />
                        <Label htmlFor="medium" className="cursor-pointer">
                          中
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="high" id="high" />
                        <Label htmlFor="high" className="cursor-pointer">
                          高
                        </Label>
                      </div>
                    </RadioGroup>
                  </div>

                  <div>
                    <Label>添付ファイル</Label>
                    <div className="mt-2">
                      <div className="flex items-center justify-center w-full">
                        <label
                          htmlFor="file-upload"
                          className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
                        >
                          <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <Paperclip className="w-8 h-8 mb-3 text-gray-400" />
                            <p className="mb-2 text-sm text-gray-500">
                              <span className="font-semibold">クリックしてアップロード</span>またはドラッグ＆ドロップ
                            </p>
                            <p className="text-xs text-gray-500">PDF、DOCX、XLSX、JPG、PNG（最大10MB）</p>
                          </div>
                          <input id="file-upload" type="file" className="hidden" multiple />
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </form>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline">下書きとして保存</Button>
              <Button>
                <Send className="h-4 w-4 mr-2" />
                リクエストを提出
              </Button>
            </CardFooter>
          </Card>
        </div>
      </main>
    </div>
  )
}
