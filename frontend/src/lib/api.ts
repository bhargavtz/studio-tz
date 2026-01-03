const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface Domain {
    domain: string;
    industry: string;
}

export interface Session {
    session_id: string;
    status: string;
    domain?: Domain;
    files_generated: string[];
    blueprint_confirmed: boolean;
    created_at: string;
    updated_at: string;
}

export interface Question {
    id: string;
    question: string;
    type: 'text' | 'textarea' | 'select' | 'multiselect' | 'yesno';
    required: boolean;
    placeholder?: string;
    options?: string[];
}

export interface Blueprint {
    pages?: {
        id: string;
        title: string;
        slug: string;
        sections?: {
            id: string;
            type: string;
            title?: string;
            components?: unknown[];
        }[];
    }[];
    theme?: {
        primaryColor: string;
        secondaryColor: string;
        accentColor: string;
        fontFamily: string;
        style: string;
    };
}

export async function createSession(vision?: string): Promise<Session> {
    const projectName = vision ? vision.slice(0, 50) : 'New Project';
    const projectVision = vision || 'A modern website';

    const response = await fetch(`${API_BASE_URL}/api/projects/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: projectName,
            vision: projectVision
        }),
    });
    if (!response.ok) throw new Error('Failed to create session');
    const data = await response.json();
    // Map project response to session format
    return {
        session_id: data.id || data.project_id || data.session_id,
        status: data.status || 'created',
        files_generated: data.files_generated || [],
        blueprint_confirmed: data.blueprint_confirmed || false,
        created_at: data.created_at || new Date().toISOString(),
        updated_at: data.updated_at || new Date().toISOString(),
    };
}

export async function getSessionStatus(sessionId: string): Promise<Session> {
    const response = await fetch(`${API_BASE_URL}/api/projects/${sessionId}`);
    if (!response.ok) throw new Error('Failed to get session status');
    const data = await response.json();
    return {
        session_id: data.id || data.project_id || sessionId,
        status: data.status || 'created',
        domain: data.domain,
        files_generated: data.files_generated || [],
        blueprint_confirmed: data.blueprint_confirmed || false,
        created_at: data.created_at || new Date().toISOString(),
        updated_at: data.updated_at || new Date().toISOString(),
    };
}

export async function processIntent(sessionId: string, intent: string) {
    const response = await fetch(`${API_BASE_URL}/api/intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, intent_text: intent }),
    });
    if (!response.ok) throw new Error('Failed to process intent');
    return response.json();
}

export async function getQuestions(sessionId: string): Promise<{ questions: Question[] }> {
    const response = await fetch(`${API_BASE_URL}/api/questions/${sessionId}`);
    if (!response.ok) throw new Error('Failed to fetch questions');
    return response.json();
}

export async function submitAnswers(sessionId: string, answers: Record<string, unknown>) {
    const response = await fetch(`${API_BASE_URL}/api/answers/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers }),
    });
    if (!response.ok) throw new Error('Failed to submit answers');
    return response.json();
}

export async function getBlueprint(sessionId: string): Promise<{ blueprint: Blueprint }> {
    const response = await fetch(`${API_BASE_URL}/api/blueprint/${sessionId}`);
    if (!response.ok) throw new Error('Failed to fetch blueprint');
    return response.json();
}

export async function confirmBlueprint(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/api/blueprint/${sessionId}/confirm`, {
        method: 'POST'
    });
    if (!response.ok) throw new Error('Failed to confirm blueprint');
    return response.json();
}

export async function generateWebsite(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/api/generate/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to generate website');
    return response.json();
}

export async function getPreviewUrl(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/api/preview/${sessionId}`);
    if (!response.ok) throw new Error('Failed to get preview url');
    return response.json();
}

export async function chatEdit(sessionId: string, message: string) {
    const response = await fetch(`${API_BASE_URL}/api/edit/${sessionId}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
    });
    if (!response.ok) {
        throw new Error('Failed to send chat message');
    }
    return response.json();
}

export async function downloadProject(sessionId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/download/${sessionId}`);
    if (!response.ok) throw new Error('Failed to download project');
    return response.blob();
}

export async function editWebsite(sessionId: string, editData: {
    edit_type: string;
    file_path: string;
    instruction: string;
    value: string;
}) {
    const response = await fetch(`${API_BASE_URL}/api/edit/${sessionId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(editData),
    });
    if (!response.ok) {
        throw new Error('Failed to edit website');
    }
    return response.json();
}

export async function getFileContent(sessionId: string, filePath: string) {
    // For now, this will be a placeholder - we'll need to implement proper file content fetching
    // The preview endpoint should return file contents
    const response = await fetch(`${API_BASE_URL}/api/preview/${sessionId}/file?path=${encodeURIComponent(filePath)}`);
    if (!response.ok) {
        // Fallback: try to get it from preview
        throw new Error(`Failed to get file content for ${filePath}`);
    }
    return response.json();
}


// Dashboard types
export interface DashboardProject {
    session_id: string;
    project_title: string;
    domain?: string;
    status: string;
    file_count: number;
    total_size_mb: number;
    thumbnail_url?: string;
    created_at: string;
    updated_at: string;
}

export interface StorageSummary {
    storage_used_mb: number;
    storage_limit_mb: number;
    usage_percentage: number;
    is_near_limit: boolean;
    is_at_limit: boolean;
}

export interface DashboardProjectsResponse {
    projects: DashboardProject[];
    pagination: {
        page: number;
        limit: number;
        total: number;
        pages: number;
    };
}

// Dashboard API functions
export async function getDashboardProjects(
    userId: string,
    page = 1,
    limit = 12,
    sortBy = 'created_at_desc',
    search?: string
): Promise<DashboardProjectsResponse> {
    const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        sort_by: sortBy,
    });
    if (search) params.append('search', search);

    const response = await fetch(`${API_BASE_URL}/api/dashboard/projects?${params}`, {
        headers: { 'Authorization': `Bearer ${userId}` },
    });
    if (!response.ok) throw new Error('Failed to fetch dashboard projects');
    return response.json();
}

export async function getStorageSummary(userId: string): Promise<StorageSummary> {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/storage`, {
        headers: { 'Authorization': `Bearer ${userId}` },
    });
    if (!response.ok) throw new Error('Failed to fetch storage summary');
    return response.json();
}

export async function deleteProject(userId: string, sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/projects/project/${sessionId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${userId}` },
    });
    if (!response.ok) throw new Error('Failed to delete project');
}

export async function renameProject(userId: string, sessionId: string, newTitle: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/projects/project/${sessionId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userId}`,
        },
        body: JSON.stringify({ project_title: newTitle }),
    });
    if (!response.ok) throw new Error('Failed to rename project');
}
