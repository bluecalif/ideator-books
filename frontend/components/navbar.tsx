"use client"

import Link from "next/link"
import { Home } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Navbar() {
  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <Link href="/library" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <Home className="h-5 w-5" />
            <span className="font-semibold text-lg">Ideator Books</span>
          </Link>
          
          <div className="flex items-center space-x-4">
            <Link href="/library">
              <Button variant="ghost" size="sm">
                라이브러리
              </Button>
            </Link>
            <Link href="/history">
              <Button variant="ghost" size="sm">
                히스토리
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

