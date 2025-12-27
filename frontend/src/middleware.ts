import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// For now, allow all routes (no protection) until you add your Clerk keys
// You can protect specific routes later by uncommenting below
// const isProtectedRoute = createRouteMatcher(['/dashboard(.*)']);

export default clerkMiddleware((auth, req) => {
    // Uncomment to protect specific routes:
    // if (isProtectedRoute(req)) auth().protect();
});

export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
        // Always run for API routes
        "/(api|trpc)(.*)",
    ],
};
