import { useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { Textarea } from "./ui/textarea"
import { createProfile, type ProfileRequest } from "@/lib/api"

interface ProfileSetupProps {
  onComplete: () => void
}

export function ProfileSetup({ onComplete }: ProfileSetupProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState<ProfileRequest>({
    ability_description: "",
    restrictions_description: "",
    goal_description: "",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await createProfile(formData)
      onComplete()
    } catch (error) {
      console.error("Failed to create profile:", error)
      alert("Failed to create profile. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Welcome to Chefing!</CardTitle>
          <p className="text-sm text-muted-foreground">
            Let's get to know you better so we can suggest the perfect recipes.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Cooking Ability
              </label>
              <Textarea
                value={formData.ability_description}
                onChange={(e) =>
                  setFormData({ ...formData, ability_description: e.target.value })
                }
                placeholder="e.g., I'm a beginner cook with limited knife skills..."
                required
                rows={3}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">
                Dietary Restrictions
              </label>
              <Textarea
                value={formData.restrictions_description}
                onChange={(e) =>
                  setFormData({ ...formData, restrictions_description: e.target.value })
                }
                placeholder="e.g., I'm lactose intolerant and avoid shellfish..."
                rows={3}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">
                Cooking Goals
              </label>
              <Textarea
                value={formData.goal_description}
                onChange={(e) =>
                  setFormData({ ...formData, goal_description: e.target.value })
                }
                placeholder="e.g., I want to eat healthier, cook faster meals..."
                rows={3}
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Setting up..." : "Get Started"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

