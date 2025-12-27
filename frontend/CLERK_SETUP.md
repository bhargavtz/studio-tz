# Clerk Authentication Setup - Instructions

## 🚨 URGENT: Fix "Cannot find middleware module" Error

**The app needs valid Clerk API keys to run!** Follow these steps **RIGHT NOW**:

### Quick Fix (5 minutes):

1. **Go to Clerk**: https://clerk.com/ → Click "Start building for free"
2. **Sign up** (or sign in if you have an account)
3. **Create Application** → Name it "NCD INAI" → Click "Create Application"
4. **Copy your keys** from the dashboard (they appear immediately)
5. **Open** `frontend/.env.local` and replace the placeholders:
   ```bash
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
   CLERK_SECRET_KEY=sk_test_your_key_here
   ```
6. **Restart the dev server**:
   - Stop the current server (press Ctrl+C in terminal, or kill process 5376)
   - Run: `npm run dev`

### ⚡ The app will NOT work until you add real keys!

---

## ✅ Installation Complete!

Clerk has been successfully integrated into your Next.js App Router application.

## 🔑 Next Steps: Get Your Clerk API Keys

### 1. Create a Clerk Account (if you haven't already)
- Visit: https://clerk.com/
- Click "Start building for free" or "Sign up"
- Complete the registration process

### 2. Create a New Application
- Once logged in, click "Create Application"
- Give your application a name (e.g., "NCD INAI")
- Select the authentication methods you want (Email, Google, GitHub, etc.)
- Click "Create Application"

### 3. Get Your API Keys
- You'll be automatically redirected to the API Keys page
- Or visit: https://dashboard.clerk.com/last-active?path=api-keys
- Copy your **Publishable Key** and **Secret Key**

### 4. Update Your Environment Variables
Open `frontend/.env.local` and replace the placeholders:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **IMPORTANT**: 
- Use **Test keys** for development (starting with `pk_test_` and `sk_test_`)
- Use **Production keys** only when deploying to production
- **NEVER** commit your `.env.local` file to git (it's already in `.gitignore`)

### 5. Restart Your Development Server
After updating the environment variables, restart your Next.js dev server:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd frontend
npm run dev
```

## 🎯 What Was Installed

### Files Created/Modified:
1. **`src/middleware.ts`** - Clerk middleware using `clerkMiddleware()`
2. **`src/app/layout.tsx`** - Updated with `<ClerkProvider>` and auth UI components
3. **`.env.local`** - Added Clerk environment variables (with placeholders)

### UI Components Added:
- **Sign In Button** - Appears when user is signed out
- **Sign Up Button** - Appears when user is signed out
- **User Button** - Appears when user is signed in (shows profile, sign out, etc.)

### Package Installed:
- `@clerk/nextjs` - Latest version of Clerk's Next.js SDK

## 🚀 Testing Your Integration

Once you've added your API keys and restarted the server:

1. Open your app at `http://localhost:3000`
2. You should see "Sign In" and "Sign Up" buttons in the header
3. Click "Sign Up" to create a test account
4. After signing up, you'll see your user avatar/button
5. Click the user button to access profile settings and sign out

## 📚 Advanced Usage

### Protecting Routes
To protect specific routes, update your `middleware.ts`:

```typescript
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/admin(.*)',
]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) await auth.protect();
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
```

### Getting User Data in Server Components
```typescript
import { auth, currentUser } from "@clerk/nextjs/server";

export default async function Page() {
  const { userId } = await auth();
  const user = await currentUser();
  
  return <div>Hello {user?.firstName}!</div>;
}
```

### Getting User Data in Client Components
```typescript
'use client';

import { useUser } from "@clerk/nextjs";

export default function Profile() {
  const { isSignedIn, user, isLoaded } = useUser();
  
  if (!isLoaded) return <div>Loading...</div>;
  if (!isSignedIn) return <div>Not signed in</div>;
  
  return <div>Hello {user.firstName}!</div>;
}
```

## 📖 Documentation
- Official Clerk Docs: https://clerk.com/docs
- Next.js Quickstart: https://clerk.com/docs/quickstarts/nextjs
- API Reference: https://clerk.com/docs/references/nextjs/overview

## ❓ Troubleshooting

### "Clerk: Missing Publishable Key"
- Make sure you've added your keys to `.env.local`
- Restart your dev server after adding environment variables

### Auth not working
- Verify keys are correct (copy directly from Clerk Dashboard)
- Check that keys start with `pk_test_` and `sk_test_` for development
- Clear browser cache and cookies

### Middleware issues
- Ensure `middleware.ts` is in the `src` directory (not in `src/app`)
- Check the matcher config includes your routes

## 🎉 You're All Set!

Your application now has enterprise-grade authentication powered by Clerk!
