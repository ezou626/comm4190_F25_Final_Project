import { useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { X, User, History, Pencil, Save, Plus, Trash2 } from "lucide-react"
import { updateProfile, type Profile, type ChatMessage } from "@/lib/api"

interface ProfilePanelProps {
  profile: Profile
  messages: ChatMessage[]
  isOpen: boolean
  onClose: () => void
  onProfileUpdate: (profile: Profile) => void
}

export function ProfilePanel({ profile, messages, isOpen, onClose, onProfileUpdate }: ProfilePanelProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedProfile, setEditedProfile] = useState<Profile>(profile)
  const [saving, setSaving] = useState(false)

  if (!isOpen) return null

  const handleStartEdit = () => {
    setEditedProfile({ ...profile })
    setIsEditing(true)
  }

  const handleCancelEdit = () => {
    setEditedProfile({ ...profile })
    setIsEditing(false)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const result = await updateProfile(editedProfile)
      onProfileUpdate(result.profile)
      setIsEditing(false)
    } catch (error) {
      console.error("Failed to update profile:", error)
      alert("Failed to save profile. Please try again.")
    } finally {
      setSaving(false)
    }
  }

  const updateField = (field: keyof Profile, index: number, value: string) => {
    setEditedProfile(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }))
  }

  const addItem = (field: keyof Profile) => {
    setEditedProfile(prev => ({
      ...prev,
      [field]: [...prev[field], ""]
    }))
  }

  const removeItem = (field: keyof Profile, index: number) => {
    setEditedProfile(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }))
  }

  const renderEditableList = (field: keyof Profile, title: string) => {
    const items = editedProfile[field]
    
    return (
      <div>
        <div className="flex items-center justify-between mb-1">
          <h4 className="text-sm font-medium">{title}:</h4>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => addItem(field)}
            className="h-6 w-6 p-0"
          >
            <Plus className="h-3 w-3" />
          </Button>
        </div>
        <div className="space-y-2">
          {items.map((item, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <Input
                value={item}
                onChange={(e) => updateField(field, idx, e.target.value)}
                className="flex-1 h-8 text-sm"
                placeholder={`Enter ${title.toLowerCase().slice(0, -1)}...`}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeItem(field, idx)}
                className="h-8 w-8 p-0 text-destructive hover:text-destructive"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))}
          {items.length === 0 && (
            <p className="text-xs text-muted-foreground italic">No items. Click + to add.</p>
          )}
        </div>
      </div>
    )
  }

  const renderReadOnlyList = (items: string[], title: string) => {
    if (items.length === 0) return null
    
    return (
      <div>
        <h4 className="text-sm font-medium mb-1">{title}:</h4>
        <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
          {items.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ol>
      </div>
    )
  }

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
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Stored Information
                </CardTitle>
                {!isEditing ? (
                  <Button variant="outline" size="sm" onClick={handleStartEdit}>
                    <Pencil className="h-3 w-3 mr-1" />
                    Edit
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCancelEdit}
                      disabled={saving}
                    >
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleSave}
                      disabled={saving}
                    >
                      <Save className="h-3 w-3 mr-1" />
                      {saving ? "Saving..." : "Save"}
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {isEditing ? (
                <>
                  {renderEditableList("long_term_instructions", "Instructions")}
                  {renderEditableList("long_term_preferences", "Preferences")}
                  {renderEditableList("long_term_restrictions", "Restrictions")}
                  {renderEditableList("long_term_situation", "Situation")}
                </>
              ) : (
                <>
                  {renderReadOnlyList(profile.long_term_instructions, "Instructions")}
                  {renderReadOnlyList(profile.long_term_preferences, "Preferences")}
                  {renderReadOnlyList(profile.long_term_restrictions, "Restrictions")}
                  {renderReadOnlyList(profile.long_term_situation, "Situation")}
                  
                  {profile.long_term_instructions.length === 0 &&
                    profile.long_term_preferences.length === 0 &&
                    profile.long_term_restrictions.length === 0 &&
                    profile.long_term_situation.length === 0 && (
                      <p className="text-sm text-muted-foreground">No profile information stored yet.</p>
                    )}
                </>
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
