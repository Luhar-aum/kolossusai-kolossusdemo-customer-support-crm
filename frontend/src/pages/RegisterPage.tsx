import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'

const schema = z.object({
  full_name: z.string().min(2),
  email: z.string().email(),
  password: z.string().min(6),
  org_name: z.string().min(2),
})
type FormData = z.infer<typeof schema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [error, setError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    setError('')
    try {
      const res = await authApi.register(data)
      const meRes = await authApi.me()
      setAuth(meRes.data, res.data.access_token)
      navigate('/dashboard')
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mx-auto mb-3">
            <span className="text-primary-foreground font-bold text-xl">C</span>
          </div>
          <h1 className="text-2xl font-bold text-foreground">Create your account</h1>
          <p className="text-muted-foreground mt-1">Start managing your sales pipeline</p>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {[
              { name: 'full_name' as const, label: 'Full Name', type: 'text', placeholder: 'Jane Smith' },
              { name: 'email' as const, label: 'Email', type: 'email', placeholder: 'jane@company.com' },
              { name: 'password' as const, label: 'Password', type: 'password', placeholder: '••••••••' },
              { name: 'org_name' as const, label: 'Organization Name', type: 'text', placeholder: 'Acme Corp' },
            ].map(({ name, label, type, placeholder }) => (
              <div key={name}>
                <label className="block text-sm font-medium text-foreground mb-1">{label}</label>
                <input
                  {...register(name)}
                  type={type}
                  placeholder={placeholder}
                  className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm"
                />
                {errors[name] && <p className="text-destructive text-xs mt-1">{errors[name]?.message}</p>}
              </div>
            ))}
            {error && <p className="text-destructive text-sm">{error}</p>}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-2 px-4 bg-primary text-primary-foreground rounded-md font-medium text-sm hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Creating account…' : 'Create account'}
            </button>
          </form>
          <div className="mt-4 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
