import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  MessageSquare, Heart, Send, ArrowLeft, Clock, User,
  Crown, Lock, Trash2, ChevronRight, Users, Reply
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ============================================
// TOPIC CARD
// ============================================
function TopicCard({ topic, onClick }) {
  const colorMap = {
    green: 'from-green-500 to-green-600',
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
    cyan: 'from-cyan-500 to-cyan-600',
    red: 'from-red-500 to-red-600',
  };

  return (
    <Card
      className="cursor-pointer hover:shadow-lg transition-all hover:-translate-y-0.5 border-0 shadow-md"
      onClick={() => onClick(topic.id)}
    >
      <CardContent className="p-5">
        <div className="flex items-start gap-4">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorMap[topic.color] || colorMap.blue} flex items-center justify-center text-2xl shadow-sm`}>
            {topic.icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-base">{topic.name}</h3>
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground mt-0.5">{topic.description}</p>
            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <MessageSquare className="w-3 h-3" />
                {topic.post_count || 0} discutii
              </span>
              {topic.last_author && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {topic.last_author}
                </span>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================
// POST CARD
// ============================================
function PostCard({ post, onOpen, onLike, onDelete, currentUserId, isPro }) {
  const timeAgo = (dateStr) => {
    const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
    if (diff < 60) return 'acum';
    if (diff < 3600) return `${Math.floor(diff / 60)}m`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
    return `${Math.floor(diff / 86400)}z`;
  };

  const isLiked = post.likes?.includes(currentUserId);
  const isAuthor = post.author_id === currentUserId;

  return (
    <Card className="border-0 shadow-sm hover:shadow-md transition-all">
      <CardContent className="p-4">
        {/* Author row */}
        <div className="flex items-center gap-2 mb-2">
          {post.author_picture ? (
            <img src={post.author_picture} alt="" className="w-7 h-7 rounded-full" />
          ) : (
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
              <User className="w-3.5 h-3.5 text-white" />
            </div>
          )}
          <span className="font-medium text-sm">{post.author_name}</span>
          <Badge variant="outline" className="text-xs px-1.5 py-0 bg-amber-50 text-amber-700 border-amber-200">
            PRO
          </Badge>
          <span className="text-xs text-muted-foreground ml-auto">{timeAgo(post.created_at)}</span>
        </div>

        {/* Title + Content */}
        {post.title && (
          <h4 className="font-semibold mb-1">{post.title}</h4>
        )}
        <p className="text-sm text-foreground/90 whitespace-pre-wrap leading-relaxed">
          {post.content.length > 300 ? post.content.slice(0, 300) + '...' : post.content}
        </p>

        {/* Actions */}
        <div className="flex items-center gap-3 mt-3 pt-2 border-t border-gray-100 dark:border-gray-800">
          <button
            onClick={(e) => { e.stopPropagation(); onLike(post.post_id); }}
            disabled={!isPro}
            className={`flex items-center gap-1 text-xs transition-colors ${
              isLiked ? 'text-red-500' : 'text-muted-foreground hover:text-red-500'
            } ${!isPro ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <Heart className={`w-3.5 h-3.5 ${isLiked ? 'fill-current' : ''}`} />
            {post.like_count || 0}
          </button>

          <button
            onClick={() => onOpen(post.post_id)}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-blue-500 cursor-pointer transition-colors"
          >
            <Reply className="w-3.5 h-3.5" />
            {post.reply_count || 0} raspunsuri
          </button>

          {isAuthor && (
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(post.post_id); }}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-red-500 cursor-pointer ml-auto transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================
// PRO PAYWALL BANNER
// ============================================
function ProWriteBanner() {
  return (
    <Card className="border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20">
      <CardContent className="p-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-amber-500 flex items-center justify-center">
          <Lock className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <p className="font-semibold text-sm">Vrei sa participi la discutii?</p>
          <p className="text-xs text-muted-foreground">Utilizatorii PRO pot scrie mesaje si raspunsuri.</p>
        </div>
        <Button size="sm" className="bg-amber-500 hover:bg-amber-600" asChild>
          <a href="/pricing">
            <Crown className="w-4 h-4 mr-1" /> Upgrade PRO
          </a>
        </Button>
      </CardContent>
    </Card>
  );
}

// ============================================
// MAIN COMPONENT
// ============================================
export default function CommunityPage() {
  const { t } = useTranslation();
  const { user, token } = useAuth();

  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(true);

  // Write state
  const [newPostContent, setNewPostContent] = useState('');
  const [newPostTitle, setNewPostTitle] = useState('');
  const [newReply, setNewReply] = useState('');
  const [posting, setPosting] = useState(false);

  const isPro = user?.subscription_level === 'pro';
  const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

  // Fetch topics
  const fetchTopics = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/community/topics`);
      if (res.ok) {
        const data = await res.json();
        setTopics(data.topics);
      }
    } catch (err) {
      console.error('Error fetching topics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch posts for a topic
  const fetchPosts = useCallback(async (topicId) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/community/topics/${topicId}/posts`);
      if (res.ok) {
        const data = await res.json();
        setPosts(data.posts);
        setSelectedTopic(data.topic);
      }
    } catch (err) {
      console.error('Error fetching posts:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch post with replies
  const fetchPostDetail = useCallback(async (postId) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/community/posts/${postId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedPost(data.post);
        setReplies(data.replies);
      }
    } catch (err) {
      console.error('Error fetching post:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTopics();
  }, [fetchTopics]);

  // Auto-refresh posts every 15s when viewing a topic
  useEffect(() => {
    if (!selectedTopic) return;
    const interval = setInterval(() => {
      if (selectedPost) {
        fetchPostDetail(selectedPost.post_id);
      } else {
        fetchPosts(selectedTopic.id);
      }
    }, 15000);
    return () => clearInterval(interval);
  }, [selectedTopic, selectedPost, fetchPosts, fetchPostDetail]);

  // Create post
  const handleCreatePost = async () => {
    if (!newPostContent.trim()) return;
    setPosting(true);
    try {
      const res = await fetch(`${API_URL}/api/community/topics/${selectedTopic.id}/posts`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: newPostContent,
          title: newPostTitle || null
        })
      });
      if (res.ok) {
        setNewPostContent('');
        setNewPostTitle('');
        fetchPosts(selectedTopic.id);
      } else {
        const err = await res.json();
        alert(err.detail);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setPosting(false);
    }
  };

  // Reply to post
  const handleReply = async () => {
    if (!newReply.trim()) return;
    setPosting(true);
    try {
      const res = await fetch(`${API_URL}/api/community/posts/${selectedPost.post_id}/reply`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newReply })
      });
      if (res.ok) {
        setNewReply('');
        fetchPostDetail(selectedPost.post_id);
      } else {
        const err = await res.json();
        alert(err.detail);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setPosting(false);
    }
  };

  // Like post
  const handleLike = async (postId) => {
    if (!isPro) return;
    try {
      const res = await fetch(`${API_URL}/api/community/posts/${postId}/like`, {
        method: 'POST',
        headers
      });
      if (res.ok) {
        // Refresh current view
        if (selectedPost) {
          fetchPostDetail(selectedPost.post_id);
        } else if (selectedTopic) {
          fetchPosts(selectedTopic.id);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Delete post
  const handleDelete = async (postId) => {
    if (!window.confirm('Sigur vrei sa stergi aceasta postare?')) return;
    try {
      const res = await fetch(`${API_URL}/api/community/posts/${postId}`, {
        method: 'DELETE',
        headers
      });
      if (res.ok) {
        if (selectedPost?.post_id === postId) {
          setSelectedPost(null);
          setReplies([]);
          fetchPosts(selectedTopic.id);
        } else {
          fetchPosts(selectedTopic.id);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Navigate back
  const goBack = () => {
    if (selectedPost) {
      setSelectedPost(null);
      setReplies([]);
      fetchPosts(selectedTopic.id);
    } else if (selectedTopic) {
      setSelectedTopic(null);
      setPosts([]);
    }
  };

  // ============================================
  // RENDER: Post Detail View
  // ============================================
  if (selectedPost) {
    const timeAgo = (dateStr) => {
      const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
      if (diff < 60) return 'acum';
      if (diff < 3600) return `${Math.floor(diff / 60)}m`;
      if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
      return `${Math.floor(diff / 86400)}z`;
    };

    return (
      <>
        <SEO title={`${selectedPost.title || 'Discutie'} | Comunitate FinRomania`} />
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
          <Button variant="ghost" size="sm" onClick={goBack}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Inapoi
          </Button>

          {/* Main post */}
          <Card className="border-0 shadow-md">
            <CardContent className="p-5">
              <div className="flex items-center gap-2 mb-3">
                {selectedPost.author_picture ? (
                  <img src={selectedPost.author_picture} alt="" className="w-8 h-8 rounded-full" />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
                <div>
                  <span className="font-medium text-sm">{selectedPost.author_name}</span>
                  <span className="text-xs text-muted-foreground ml-2">{timeAgo(selectedPost.created_at)}</span>
                </div>
                <Badge variant="outline" className="text-xs px-1.5 py-0 bg-amber-50 text-amber-700 border-amber-200">PRO</Badge>
              </div>

              {selectedPost.title && <h2 className="text-lg font-bold mb-2">{selectedPost.title}</h2>}
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{selectedPost.content}</p>
            </CardContent>
          </Card>

          {/* Replies */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-muted-foreground px-1">
              {replies.length} {replies.length === 1 ? 'raspuns' : 'raspunsuri'}
            </h3>

            {replies.map((reply) => (
              <Card key={reply.post_id} className="border-0 shadow-sm ml-4 border-l-2 border-l-blue-200">
                <CardContent className="p-3">
                  <div className="flex items-center gap-2 mb-1">
                    {reply.author_picture ? (
                      <img src={reply.author_picture} alt="" className="w-6 h-6 rounded-full" />
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-blue-500 flex items-center justify-center">
                        <User className="w-3 h-3 text-white" />
                      </div>
                    )}
                    <span className="font-medium text-xs">{reply.author_name}</span>
                    <span className="text-xs text-muted-foreground">{timeAgo(reply.created_at)}</span>
                    {reply.author_id === user?.user_id && (
                      <button onClick={() => handleDelete(reply.post_id)} className="ml-auto text-muted-foreground hover:text-red-500">
                        <Trash2 className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                  <p className="text-sm whitespace-pre-wrap">{reply.content}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Reply form or paywall */}
          {isPro ? (
            <div className="flex gap-2">
              <input
                value={newReply}
                onChange={(e) => setNewReply(e.target.value)}
                placeholder="Scrie un raspuns..."
                className="flex-1 px-3 py-2 rounded-lg border bg-background text-sm"
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleReply()}
              />
              <Button onClick={handleReply} disabled={posting || !newReply.trim()} size="sm">
                <Send className="w-4 h-4" />
              </Button>
            </div>
          ) : (
            <ProWriteBanner />
          )}
        </div>
      </>
    );
  }

  // ============================================
  // RENDER: Topic Posts View
  // ============================================
  if (selectedTopic) {
    return (
      <>
        <SEO title={`${selectedTopic.name} | Comunitate FinRomania`} />
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={goBack}>
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <span className="text-2xl">{selectedTopic.icon}</span>
            <div>
              <h1 className="text-xl font-bold">{selectedTopic.name}</h1>
              <p className="text-sm text-muted-foreground">{selectedTopic.description}</p>
            </div>
          </div>

          {/* New post form (PRO only) */}
          {isPro ? (
            <Card className="border-0 shadow-md">
              <CardContent className="p-4 space-y-2">
                <input
                  value={newPostTitle}
                  onChange={(e) => setNewPostTitle(e.target.value)}
                  placeholder="Titlu (optional)"
                  className="w-full px-3 py-2 rounded-lg border bg-background text-sm font-medium"
                />
                <textarea
                  value={newPostContent}
                  onChange={(e) => setNewPostContent(e.target.value)}
                  placeholder="Ce vrei sa discuti?"
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg border bg-background text-sm resize-none"
                />
                <div className="flex justify-end">
                  <Button
                    onClick={handleCreatePost}
                    disabled={posting || !newPostContent.trim()}
                    size="sm"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    {posting ? 'Se posteaza...' : 'Posteaza'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <ProWriteBanner />
          )}

          {/* Posts list */}
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Se incarca...</div>
          ) : posts.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="font-medium">Inca nu sunt discutii</p>
              <p className="text-sm mt-1">Fii primul care deschide o discutie!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {posts.map((post) => (
                <PostCard
                  key={post.post_id}
                  post={post}
                  onOpen={fetchPostDetail}
                  onLike={handleLike}
                  onDelete={handleDelete}
                  currentUserId={user?.user_id}
                  isPro={isPro}
                />
              ))}
            </div>
          )}
        </div>
      </>
    );
  }

  // ============================================
  // RENDER: Topics Overview
  // ============================================
  return (
    <>
      <SEO
        title="Comunitate | FinRomania"
        description="Discuta cu alti investitori romani despre BVB, dividende, strategii si taxe."
      />
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mx-auto shadow-lg">
            <Users className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold">Comunitate</h1>
          <p className="text-sm text-muted-foreground max-w-md mx-auto">
            Discuta cu alti investitori romani. Intreaba, imparte experienta, invata impreuna.
          </p>
          {!isPro && (
            <Badge variant="outline" className="text-xs bg-amber-50 text-amber-700 border-amber-200">
              <Lock className="w-3 h-3 mr-1" />
              Citesti gratuit. PRO pentru a scrie.
            </Badge>
          )}
        </div>

        {/* Topics grid */}
        {loading ? (
          <div className="text-center py-8 text-muted-foreground">Se incarca...</div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {topics.map((topic) => (
              <TopicCard
                key={topic.id}
                topic={topic}
                onClick={(id) => fetchPosts(id)}
              />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
