import { Button } from "./ui/button"
import { Plus, MessageSquare, ChevronLeft, ChevronRight } from "lucide-react"
import type { Conversation } from "@/lib/api"
import { cn } from "@/lib/utils"

interface ConversationsListProps {
  conversations: Conversation[]
  currentConversationId: number | null
  onSelectConversation: (id: number) => void
  onCreateConversation: () => void
  isCollapsed: boolean
  onToggleCollapse: () => void
}

function formatDate(dateString: string): string {
  if (!dateString) return ""
  
  const date = new Date(dateString)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
  const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  
  if (dateOnly.getTime() === today.getTime()) {
    return "Today"
  } else if (dateOnly.getTime() === yesterday.getTime()) {
    return "Yesterday"
  } else if (now.getTime() - date.getTime() < 7 * 24 * 60 * 60 * 1000) {
    // Within last 7 days, show day name
    return date.toLocaleDateString("en-US", { weekday: "long" })
  } else {
    // Older, show date
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
  }
}

// Group conversations by date
function groupConversationsByDate(conversations: Conversation[]): { date: string; conversations: Conversation[] }[] {
  const groups: { [key: string]: Conversation[] } = {}
  
  conversations.forEach((conv) => {
    const dateKey = formatDate(conv.updated_at || conv.created_at)
    if (!groups[dateKey]) {
      groups[dateKey] = []
    }
    groups[dateKey].push(conv)
  })
  
  // Convert to array maintaining order
  const dateOrder = ["Today", "Yesterday"]
  const result: { date: string; conversations: Conversation[] }[] = []
  
  // Add known date groups first
  dateOrder.forEach((date) => {
    if (groups[date]) {
      result.push({ date, conversations: groups[date] })
      delete groups[date]
    }
  })
  
  // Add remaining groups (day names and dates)
  Object.keys(groups).forEach((date) => {
    result.push({ date, conversations: groups[date] })
  })
  
  return result
}

export function ConversationsList({
  conversations,
  currentConversationId,
  onSelectConversation,
  onCreateConversation,
  isCollapsed,
  onToggleCollapse,
}: ConversationsListProps) {
  if (isCollapsed) {
    return (
      <div className="border-r bg-muted/30 flex flex-col">
        <div className="p-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleCollapse}
            className="w-full"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    )
  }

  const groupedConversations = groupConversationsByDate(conversations)

  return (
    <div className="w-64 border-r bg-muted/30 flex flex-col">
      <div className="p-4 border-b flex items-center gap-2">
        <Button
          variant="default"
          size="sm"
          className="flex-1"
          onClick={onCreateConversation}
        >
          <Plus className="h-4 w-4 mr-2" />
          New Chat
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleCollapse}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto">
        <div className="p-2">
          {conversations.length === 0 ? (
            <p className="text-sm text-muted-foreground p-2 text-center">
              No conversations yet
            </p>
          ) : (
            groupedConversations.map((group) => (
              <div key={group.date} className="mb-4">
                <p className="text-xs font-medium text-muted-foreground px-2 py-1 uppercase tracking-wider">
                  {group.date}
                </p>
                <div className="space-y-1">
                  {group.conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => onSelectConversation(conv.id)}
                      className={cn(
                        "w-full text-left p-3 rounded-md text-sm transition-colors",
                        "hover:bg-accent hover:text-accent-foreground",
                        currentConversationId === conv.id
                          ? "bg-accent text-accent-foreground font-medium"
                          : "text-muted-foreground"
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="truncate">{conv.title || "New Chat"}</p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
