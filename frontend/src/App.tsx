import { useState, useEffect, useRef } from "react"
import { ChatMessage } from "./components/ChatMessage"
import { ChatInput } from "./components/ChatInput"
import { ProfileSetup } from "./components/ProfileSetup"
import { ProfilePanel } from "./components/ProfilePanel"
import { ConversationsList } from "./components/ConversationsList"
import {
  getProfile,
  sendChatMessage,
  getConversations,
  createConversation,
  getConversationMessages,
  resetDemo,
  type ChatMessage as ChatMessageType,
  type Profile,
  type Conversation,
} from "./lib/api"
import { ChefHat, User, RotateCcw, Menu } from "lucide-react"
import { Button } from "./components/ui/button"

function App() {
  const [profileLoaded, setProfileLoaded] = useState(false)
  const [showProfileSetup, setShowProfileSetup] = useState(false)
  const [showProfilePanel, setShowProfilePanel] = useState(false)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [pendingMessages, setPendingMessages] = useState<Map<number, { message: string; image?: File }>>(new Map())
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const pendingIdRef = useRef(0)

  useEffect(() => {
    checkProfile()
    loadConversations()
  }, [])

  useEffect(() => {
    if (currentConversationId) {
      loadConversationMessages(currentConversationId)
    } else {
      setMessages([])
    }
  }, [currentConversationId])

  useEffect(() => {
    scrollToBottom()
  }, [messages, pendingMessages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const checkProfile = async () => {
    try {
      const profileData = await getProfile()
      setProfile(profileData)
      const hasProfile =
        profileData.long_term_instructions.length > 0 ||
        profileData.long_term_preferences.length > 0 ||
        profileData.long_term_restrictions.length > 0 ||
        profileData.long_term_situation.length > 0

      setShowProfileSetup(!hasProfile)
      setProfileLoaded(true)
    } catch (error) {
      console.error("Failed to load profile:", error)
      setShowProfileSetup(true)
      setProfileLoaded(true)
    }
  }

  const loadConversations = async () => {
    try {
      const convs = await getConversations()
      setConversations(convs)
      // Don't auto-select - start with a new chat on refresh
      // Conversation will be created when user sends first message
    } catch (error) {
      console.error("Failed to load conversations:", error)
    }
  }

  const loadConversationMessages = async (conversationId: number) => {
    try {
      const msgs = await getConversationMessages(conversationId)
      setMessages(msgs)
    } catch (error) {
      console.error("Failed to load conversation messages:", error)
    }
  }

  const handleCreateConversation = async () => {
    try {
      const newConv = await createConversation()
      setConversations((prev) => [newConv, ...prev])
      setCurrentConversationId(newConv.id)
      setMessages([])
    } catch (error) {
      console.error("Failed to create conversation:", error)
      alert("Failed to create new conversation. Please try again.")
    }
  }

  const handleSelectConversation = (id: number) => {
    setCurrentConversationId(id)
  }

  const handleSend = async (message: string, image?: File) => {
    if (!message.trim() && !image) return

    // Create new conversation if none exists
    let convId = currentConversationId
    if (!convId) {
      try {
        const newConv = await createConversation()
        convId = newConv.id
        setCurrentConversationId(convId)
        setConversations((prev) => [newConv, ...prev])
      } catch (error) {
        console.error("Failed to create conversation:", error)
        alert("Failed to create conversation. Please try again.")
        return
      }
    }

    // Create optimistic message
    const pendingId = pendingIdRef.current++
    let imagePreviewUrl: string | null = null
    if (image) {
      imagePreviewUrl = URL.createObjectURL(image)
    }

    const tempMessage: ChatMessageType = {
      id: -pendingId, // Negative ID to distinguish from real messages
      message: message || "Fridge image",
      response: {},
      has_image: !!image,
      image_path: imagePreviewUrl, // Use preview URL temporarily
      created_at: new Date().toISOString(),
    }

    // Add to messages immediately (optimistic UI)
    setMessages((prev) => [...prev, tempMessage])
    setPendingMessages((prev) => {
      const newMap = new Map(prev)
      newMap.set(pendingId, { message, image })
      return newMap
    })

    setLoading(true)
    try {
      await sendChatMessage(message, image, convId)

      // Reload conversation messages
      await loadConversationMessages(convId)
      // Reload conversations to update titles and counts
      await loadConversations()

      // Reload profile to get updates
      const profileData = await getProfile()
      setProfile(profileData)
    } catch (error) {
      console.error("Failed to send message:", error)
      // Remove the optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempMessage.id))
      alert("Failed to send message. Please try again.")
    } finally {
      // Clean up blob URL if it was created
      if (imagePreviewUrl) {
        URL.revokeObjectURL(imagePreviewUrl)
      }
      setLoading(false)
      setPendingMessages((prev) => {
        const newMap = new Map(prev)
        newMap.delete(pendingId)
        return newMap
      })
    }
  }

  const handleProfileComplete = () => {
    setShowProfileSetup(false)
    checkProfile()
  }

  const handleReset = async () => {
    if (
      !confirm(
        "Are you sure you want to reset the demo? This will clear all chat history, profile data, and feedback. This action cannot be undone."
      )
    ) {
      return
    }

    try {
      await resetDemo()
      // Clear local state
      setMessages([])
      setConversations([])
      setCurrentConversationId(null)
      setProfile(null)
      // Reload profile to show setup screen
      await checkProfile()
      alert("Demo reset successfully!")
    } catch (error) {
      console.error("Failed to reset demo:", error)
      alert("Failed to reset demo. Please try again.")
    }
  }

  if (!profileLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ChefHat className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (showProfileSetup) {
    return <ProfileSetup onComplete={handleProfileComplete} />
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Conversations Sidebar */}
      <ConversationsList
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onCreateConversation={handleCreateConversation}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {sidebarCollapsed && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSidebarCollapsed(false)}
                  className="mr-2"
                >
                  <Menu className="h-4 w-4" />
                </Button>
              )}
              <ChefHat className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-semibold">Chefing</h1>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowProfilePanel(true)}
              >
                <User className="h-4 w-4 mr-2" />
                Profile
              </Button>
              <Button variant="outline" size="sm" onClick={handleReset}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset
              </Button>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && pendingMessages.size === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <ChefHat className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Start a conversation by sending a message or uploading a fridge image!</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => {
                const isPending = message.id < 0 && pendingMessages.has(-message.id)
                return (
                  <ChatMessage
                    key={message.id}
                    message={message}
                    isPending={isPending}
                  />
                )
              })}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>

      {/* Profile Panel */}
      {profile && (
        <ProfilePanel
          profile={profile}
          messages={messages.filter((m) => m.id > 0)}
          isOpen={showProfilePanel}
          onClose={() => setShowProfilePanel(false)}
          onProfileUpdate={(updatedProfile) => setProfile(updatedProfile)}
        />
      )}
    </div>
  )
}

export default App
