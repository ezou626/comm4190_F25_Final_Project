import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { X, User, History } from "lucide-react"
import type { Profile, ChatMessage } from "@/lib/api"

interface ProfilePanelProps {
  profile: Profile
  messages: ChatMessage[]
  isOpen: boolean
  onClose: () => void
}

export function ProfilePanel({ profile, messages, isOpen, onClose }: ProfilePanelProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/50" onClick={onClose}>
      <div
        className="absolute right-0 top-0 h-full w-full max-w-md bg-background border-l shadow-lg overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">Your Profile</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="p-4 space-y-4">
          {/* Profile Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <User className="h-4 w-4" />
                Stored Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {profile.long_term_instructions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-1">Instructions:</h4>
                  <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                    {profile.long_term_instructions.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ol>
                </div>
              )}

              {profile.long_term_preferences.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-1">Preferences:</h4>
                  <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                    {profile.long_term_preferences.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ol>
                </div>
              )}

              {profile.long_term_restrictions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-1">Restrictions:</h4>
                  <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                    {profile.long_term_restrictions.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ol>
                </div>
              )}

              {profile.long_term_situation.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-1">Situation:</h4>
                  <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                    {profile.long_term_situation.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ol>
                </div>
              )}

              {profile.long_term_instructions.length === 0 &&
                profile.long_term_preferences.length === 0 &&
                profile.long_term_restrictions.length === 0 &&
                profile.long_term_situation.length === 0 && (
                  <p className="text-sm text-muted-foreground">No profile information stored yet.</p>
                )}
            </CardContent>
          </Card>

          {/* Chat History Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <History className="h-4 w-4" />
                Chat History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {messages.length} {messages.length === 1 ? "conversation" : "conversations"}
              </p>
              {messages.length > 0 && (
                <div className="mt-2 space-y-2">
                  {messages.slice(0, 5).map((msg) => (
                    <div key={msg.id} className="text-xs text-muted-foreground p-2 bg-muted rounded">
                      <p className="truncate">{msg.message}</p>
                      {msg.response?.recipe && (
                        <p className="text-xs mt-1">Recipe: {msg.response.recipe.name}</p>
                      )}
                    </div>
                  ))}
                  {messages.length > 5 && (
                    <p className="text-xs text-muted-foreground">...and {messages.length - 5} more</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

