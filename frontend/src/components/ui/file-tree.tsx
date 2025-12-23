"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import {
    ChevronRight,
    ChevronDown,
    Folder,
    FolderOpen,
    File,
    FileCode,
    FileJson,
    FileImage,
    FileText
} from "lucide-react"

interface FileNode {
    name: string
    type: "file" | "folder"
    children?: FileNode[]
    extension?: string
}

interface FileTreeProps {
    data: FileNode[]
    className?: string
    onFileSelect?: (path: string) => void
}

interface FileItemProps {
    node: FileNode
    depth: number
    currentPath: string
    onFileSelect?: (path: string) => void
    activePath?: string
}

const getFileIcon = (extension?: string) => {
    switch (extension) {
        case 'html': return <FileCode className="w-4 h-4 text-orange-500" />;
        case 'css': return <FileCode className="w-4 h-4 text-blue-400" />;
        case 'js':
        case 'jsx':
        case 'ts':
        case 'tsx': return <FileCode className="w-4 h-4 text-yellow-400" />;
        case 'json': return <FileJson className="w-4 h-4 text-green-400" />;
        case 'png':
        case 'jpg':
        case 'svg': return <FileImage className="w-4 h-4 text-purple-400" />;
        default: return <FileText className="w-4 h-4 text-gray-400" />;
    }
}

function FileItem({ node, depth, currentPath, onFileSelect, activePath }: FileItemProps) {
    const [isOpen, setIsOpen] = useState(true)
    const [isHovered, setIsHovered] = useState(false)

    const isFolder = node.type === "folder"
    const hasChildren = isFolder && node.children && node.children.length > 0
    const fullPath = currentPath ? `${currentPath}/${node.name}` : node.name
    const isActive = activePath === fullPath

    const handleClick = (e: React.MouseEvent) => {
        e.stopPropagation()
        if (isFolder) {
            setIsOpen(!isOpen)
        } else {
            onFileSelect?.(fullPath)
        }
    }

    return (
        <div className="select-none">
            <div
                className={cn(
                    "group flex items-center gap-1 py-1 px-2 cursor-pointer text-zinc-400 hover:text-zinc-100 transition-colors",
                    isActive && "bg-white/10 text-white"
                )}
                onClick={handleClick}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                style={{ paddingLeft: `${depth * 12 + 10}px` }}
            >
                {/* Folder Chevron */}
                <div className="w-4 flex items-center justify-center shrink-0">
                    {isFolder && (
                        isOpen ? (
                            <ChevronDown className="w-3.5 h-3.5" />
                        ) : (
                            <ChevronRight className="w-3.5 h-3.5" />
                        )
                    )}
                </div>

                {/* Icon */}
                <div className="shrink-0 flex items-center justify-center">
                    {isFolder ? (
                        isOpen ? (
                            <FolderOpen className={cn("w-4 h-4", hasChildren ? "text-indigo-400" : "text-zinc-500")} />
                        ) : (
                            <Folder className={cn("w-4 h-4", hasChildren ? "text-indigo-400" : "text-zinc-500")} />
                        )
                    ) : (
                        getFileIcon(node.extension)
                    )}
                </div>

                {/* Name */}
                <span className={cn(
                    "font-medium text-[13px] truncate ml-1.5",
                    isActive ? "text-white" : "text-zinc-400 group-hover:text-zinc-200"
                )}>
                    {node.name}
                </span>
            </div>

            {/* Children */}
            {hasChildren && isOpen && (
                <div>
                    {node.children!.map((child) => (
                        <FileItem
                            key={child.name}
                            node={child}
                            depth={depth + 1}
                            currentPath={fullPath}
                            onFileSelect={onFileSelect}
                            activePath={activePath}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

export function FileTree({ data, className, onFileSelect }: FileTreeProps) {
    // We need to know which file is active to highlight it. 
    // Ideally this would come from props, but for now we'll handle internal select state matching.
    const [activePath, setActivePath] = useState<string>("")

    const handleSelect = (path: string) => {
        setActivePath(path)
        onFileSelect?.(path)
    }

    // Default expand all by rendering
    return (
        <div className={cn("font-sans", className)}>
            <div className="flex items-center gap-2 px-3 py-2">
                <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">Explorer</span>
            </div>

            <div className="flex flex-col">
                {data.map((node) => (
                    <FileItem
                        key={node.name}
                        node={node}
                        depth={0}
                        currentPath=""
                        onFileSelect={handleSelect}
                        activePath={activePath}
                    />
                ))}
            </div>
        </div>
    )
}
