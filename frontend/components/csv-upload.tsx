'use client'

import { useState, useCallback } from 'react'
import { Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { toast } from 'sonner'

interface CSVUploadProps {
  onUploadSuccess: () => void
}

export function CSVUpload({ onUploadSuccess }: CSVUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true)
    } else if (e.type === 'dragleave') {
      setIsDragging(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files?.[0]) {
      if (files[0].name.endsWith('.csv')) {
        setFile(files[0])
      } else {
        toast.error('CSV 파일만 업로드 가능합니다')
      }
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files?.[0]) {
      setFile(files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    try {
      const { api } = await import('@/lib/api')
      await api.uploadCSV(file)
      toast.success(`${file.name} 업로드 완료`)
      setFile(null)
      onUploadSuccess()
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('업로드 실패')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Card className="p-6">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-sm text-gray-600 mb-2">
          CSV 파일을 드래그하거나 클릭하여 선택하세요
        </p>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileInput}
          className="hidden"
          id="csv-file-input"
        />
        <label htmlFor="csv-file-input">
          <Button variant="outline" className="cursor-pointer" asChild>
            <span>파일 선택</span>
          </Button>
        </label>

        {file && (
          <div className="mt-4 p-3 bg-gray-50 rounded">
            <p className="text-sm font-medium text-gray-700">{file.name}</p>
            <p className="text-xs text-gray-500">
              {(file.size / 1024).toFixed(2)} KB
            </p>
          </div>
        )}
      </div>

      {file && (
        <div className="mt-4 flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => setFile(null)}
            disabled={uploading}
          >
            취소
          </Button>
          <Button onClick={handleUpload} disabled={uploading}>
            {uploading ? '업로드 중...' : '업로드'}
          </Button>
        </div>
      )}
    </Card>
  )
}

