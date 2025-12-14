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
        <div className="p-2 space-y-1">
          {conversations.length === 0 ? (
            <p className="text-sm text-muted-foreground p-2 text-center">
              No conversations yet
            </p>
          ) : (
            conversations.map((conv) => (
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
                    <p className="truncate">{conv.title}</p>
                    {conv.message_count > 0 && (
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {conv.message_count} {conv.message_count === 1 ? "message" : "messages"}
                      </p>
                    )}
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

