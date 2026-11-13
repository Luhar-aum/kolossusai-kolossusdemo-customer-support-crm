import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { useThemeStore } from '@/store/themeStore'
import { Sun, Moon } from 'lucide-react'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
})

type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const { theme, toggleTheme } = useThemeStore()
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [error, setError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    setError('')
    try {
      const res = await authApi.login(data)
      const meRes = await authApi.me()
      setAuth(meRes.data, res.data.access_token)
      navigate('/dashboard')
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Login failed')
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 p-2 rounded-md hover:bg-accent text-muted-foreground transition-colors"
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mx-auto mb-3">
            <span className="text-primary-foreground font-bold text-xl">C</span>
          </div>
          <h1 className="text-2xl font-bold text-foreground">Welcome back</h1>
          <p className="text-muted-foreground mt-1">Sign in to your CRM</p>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Email</label>
              <input
                {...register('email')}
                type="email"
                placeholder="you@company.com"
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm"
              />
              {errors.email && <p className="text-destructive text-xs mt-1">{errors.email.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">Password</label>
              <input
                {...register('password')}
                type="password"
                placeholder="••••••••"
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm"
              />
              {errors.password && <p className="text-destructive text-xs mt-1">{errors.password.message}</p>}
            </div>
            {error && <p className="text-destructive text-sm">{error}</p>}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-2 px-4 bg-primary text-primary-foreground rounded-md font-medium text-sm hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <div className="mt-4 text-center text-sm text-muted-foreground">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary hover:underline">Register</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
