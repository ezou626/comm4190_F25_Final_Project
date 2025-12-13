import type { ChatMessage as ChatMessageType } from "@/lib/api"
import { Card, CardContent } from "./ui/card"
import { ChefHat, User } from "lucide-react"

interface ChatMessageProps {
  message: ChatMessageType
  isPending?: boolean
}

export function ChatMessage({ message, isPending = false }: ChatMessageProps) {
  const hasRecipe = message.response?.recipe
  const recipe = hasRecipe ? message.response.recipe : null

  return (
    <div className="space-y-4">
      {/* User Message */}
      <div className="flex gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <User className="h-4 w-4" />
        </div>
        <Card className="flex-1">
          <CardContent className="p-4">
            <p className="text-sm">{message.message}</p>
            {message.has_image && message.image_path && (
              <div className="mt-2">
                <img
                  src={message.image_path.startsWith('blob:') || message.image_path.startsWith('data:') 
                    ? message.image_path 
                    : `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/${message.image_path}`}
                  alt="Fridge contents"
                  className="max-w-xs rounded-md"
                />
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Assistant Response */}
      {!isPending && (
        <div className="flex gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
            <ChefHat className="h-4 w-4" />
          </div>
          <Card className="flex-1">
            <CardContent className="p-4">
              {hasRecipe ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold">{recipe.name}</h3>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Ingredients:</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {recipe.ingredients.map((ing: string, idx: number) => (
                        <li key={idx}>{ing}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Steps:</h4>
                    <ol className="space-y-2 text-sm list-decimal list-inside">
                      {recipe.steps.map((step: string, idx: number) => (
                        <li key={idx} className="pl-2">{step}</li>
                      ))}
                    </ol>
                  </div>
                </div>
              ) : (
                <div className="text-sm">
                  {message.response?.parsed_info && (
                    <div className="space-y-2">
                      <p>I've noted your preferences and updated your profile.</p>
                      {Object.entries(message.response.parsed_info).some(([_, v]) => Array.isArray(v) && v.length > 0) && (
                        <div className="mt-2 text-xs text-muted-foreground">
                          <p>New information recorded:</p>
                          <ul className="list-disc list-inside mt-1">
                            {message.response.parsed_info.new_instructions?.length > 0 && (
                              <li>Instructions: {message.response.parsed_info.new_instructions.join(", ")}</li>
                            )}
                            {message.response.parsed_info.new_preferences?.length > 0 && (
                              <li>Preferences: {message.response.parsed_info.new_preferences.join(", ")}</li>
                            )}
                            {message.response.parsed_info.new_restrictions?.length > 0 && (
                              <li>Restrictions: {message.response.parsed_info.new_restrictions.join(", ")}</li>
                            )}
                            {message.response.parsed_info.new_situation?.length > 0 && (
                              <li>Situation: {message.response.parsed_info.new_situation.join(", ")}</li>
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Loading indicator for pending messages */}
      {isPending && (
        <div className="flex gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
            <ChefHat className="h-4 w-4" />
          </div>
          <Card className="flex-1">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-muted-foreground rounded-full animate-pulse" />
                <div className="h-2 w-2 bg-muted-foreground rounded-full animate-pulse delay-75" />
                <div className="h-2 w-2 bg-muted-foreground rounded-full animate-pulse delay-150" />
                <span className="text-sm text-muted-foreground ml-2">Thinking...</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
