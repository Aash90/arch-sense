/**
 * Shared type definitions for arch-sense server
 */

export enum ComponentType {
  LOAD_BALANCER = 'LOAD_BALANCER',
  L4_LOAD_BALANCER = 'L4_LOAD_BALANCER',
  L7_LOAD_BALANCER = 'L7_LOAD_BALANCER',
  API_GATEWAY = 'API_GATEWAY',
  MICROSERVICE = 'MICROSERVICE',
  DATABASE = 'DATABASE',
  CACHE = 'CACHE',
  MESSAGE_QUEUE = 'MESSAGE_QUEUE',
  CDN = 'CDN',
  EXTERNAL_SERVICE = 'EXTERNAL_SERVICE',
  COMMENT = 'COMMENT',
}

export interface SystemNode {
  id: string;
  type: ComponentType;
  x: number;
  y: number;
  label: string;
  properties: Record<string, any>;
}

export interface SystemEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export interface SimulationState {
  phase: 'PROBLEM_STATEMENT' | 'DESIGN' | 'STRESS' | 'EVALUATION';
  scenario: string;
  stressEvents: StressEvent[];
  currentStressIndex: number;
}

export interface StressEvent {
  id: string;
  title: string;
  description: string;
  impact: string;
  triggered: boolean;
}

export interface Message {
  id: string;
  role: 'architect' | 'user';
  content: string;
  timestamp: number;
}

export interface Evaluation {
  scalability: number;
  reliability: number;
  clarity: number;
  feedback: string;
  strengths: string[];
  weaknesses: string[];
}

export type DesignSignal =
  | 'HAS_MESSAGE_QUEUE'
  | 'DIRECT_EXTERNAL_CALL'
  | 'ASYNC_PROCESSING'
  | 'SPOF_DATABASE'
  | 'NO_LOAD_BALANCER';

// Session State for persistence
export interface SessionData {
  id: string;
  nodes: SystemNode[];
  edges: SystemEdge[];
  phase: 'PROBLEM_STATEMENT' | 'DESIGN' | 'STRESS' | 'EVALUATION';
  scenario: string;
  scalingChallenge: string;
  signals: DesignSignal[];
  messages: Message[];
  evaluation: Evaluation | null;
  stressEvents: StressEvent[];
  currentStressIndex: number;
  createdAt: number;
  updatedAt: number;
}

// API Request/Response types
export interface UpdateSessionRequest {
  nodes?: SystemNode[];
  edges?: SystemEdge[];
  phase?: SimulationState['phase'];
  scalingChallenge?: string;
  signals?: DesignSignal[];
  messages?: Message[];
  stressEvents?: StressEvent[];
  currentStressIndex?: number;
}

export interface ArchitectFeedbackRequest {
  nodes: SystemNode[];
  edges: SystemEdge[];
  history: Message[];
  phase: string;
  scenario: string;
  scalingChallenge: string;
}

export interface FinalEvaluationRequest {
  nodes: SystemNode[];
  edges: SystemEdge[];
  history: Message[];
  scenario: string;
  scalingChallenge: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}
