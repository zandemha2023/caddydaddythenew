export type AgentType = 'requirements' | 'cad' | 'validation' | 'export';

export type MessageStatus = 'thinking' | 'complete' | 'error';

export type DesignStatus = 'processing' | 'awaiting_clarification' | 'complete' | 'failed';

export interface AgentMessage {
  id: string;
  agentType: AgentType;
  content: string;
  timestamp: Date;
  status: MessageStatus;
  details?: string;
  metadata?: Record<string, any>;
}

export interface DesignSession {
  id: string;
  prompt: string;
  status: DesignStatus;
  messages: AgentMessage[];
  fileUrl?: string;
  createdAt: Date;
  updatedAt?: Date;
  progress?: number;
  currentAgent?: AgentType;
}

export interface WebSocketMessage {
  type: 'agent_thinking' | 'progress' | 'code_generated' | 'complete' | 'error' | 'connected';
  job_id?: string;
  agent?: AgentType;
  thinking?: string;
  progress?: number;
  stage?: string;
  message?: string;
  code?: string;
  code_type?: string;
  success?: boolean;
  result?: any;
  error?: string;
  timestamp?: string;
  metadata?: Record<string, any>;
}

export interface DesignRequest {
  prompt: string;
  project_id?: string;
}

export interface DesignProcessRequest {
  session_id: string;
  message: string;
}

export interface DesignStartResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface DesignProcessResponse {
  session_id: string;
  status: DesignStatus;
  questions?: string[];
  confidence?: number;
  message?: string;
  design_id?: string;
  file_id?: string;
  file_path?: string;
  download_url?: string;
}

export interface DesignStatusResponse {
  session_id: string;
  status: DesignStatus;
  current_agent?: AgentType;
  design_id?: string;
  has_requirements: boolean;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: Date;
  updated_at: Date;
}

export interface Design {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  original_prompt: string;
  created_at: Date;
  updated_at: Date;
}

export interface CADFile {
  id: string;
  filename: string;
  file_format: 'STL' | 'STEP' | 'OBJ' | 'DXF';
  file_size: number;
  file_path: string;
  is_primary: boolean;
  created_at: Date;
}
