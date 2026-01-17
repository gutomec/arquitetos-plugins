// SDR Virtual Dashboard - Main Component
// Use with Claude Code artifact system or standalone React app

import React, { useState, useEffect } from 'react';

// Types
interface Lead {
  id: string;
  remoteJid: string;
  contactName: string;
  score: number;
  stage: string;
  intent: string;
  lastMessage: string;
  waitingMinutes: number;
  estimatedValue: number;
}

interface Metrics {
  messagesReceived: number;
  messagesSent: number;
  hotLeads: number;
  opportunities: number;
  avgResponseTime: number;
  slaRate: number;
  revenue: number;
  conversions: number;
}

interface ForgottenChat {
  id: string;
  remoteJid: string;
  contactName: string;
  waitingMinutes: number;
  score: number;
  lastMessage: string;
  classification: string;
}

// Mock data for demonstration
const mockMetrics: Metrics = {
  messagesReceived: 147,
  messagesSent: 89,
  hotLeads: 8,
  opportunities: 23,
  avgResponseTime: 18,
  slaRate: 87.5,
  revenue: 52300,
  conversions: 7
};

const mockHotLeads: Lead[] = [
  {
    id: '1',
    remoteJid: '5511999999999@s.whatsapp.net',
    contactName: 'Maria Santos',
    score: 92,
    stage: 'OPPORTUNITY',
    intent: 'COMPRA',
    lastMessage: 'Quanto custa o servico de consultoria?',
    waitingMinutes: 3,
    estimatedValue: 15000
  },
  {
    id: '2',
    remoteJid: '5511888888888@s.whatsapp.net',
    contactName: 'Joao Silva',
    score: 87,
    stage: 'PROPOSAL',
    intent: 'COMPRA',
    lastMessage: 'Preciso urgente para hoje',
    waitingMinutes: 8,
    estimatedValue: 8500
  },
  {
    id: '3',
    remoteJid: '5511777777777@s.whatsapp.net',
    contactName: 'Pedro Costa',
    score: 85,
    stage: 'OPPORTUNITY',
    intent: 'COMPRA',
    lastMessage: 'Aceita pix? Quero fechar agora',
    waitingMinutes: 15,
    estimatedValue: 12000
  }
];

const mockForgottenChats: ForgottenChat[] = [
  {
    id: '1',
    remoteJid: '5511666666666@s.whatsapp.net',
    contactName: 'Ana Oliveira',
    waitingMinutes: 154,
    score: 45,
    lastMessage: 'Pode me ligar quando puder?',
    classification: 'FOLLOW_UP'
  },
  {
    id: '2',
    remoteJid: '5511555555555@s.whatsapp.net',
    contactName: 'Carlos Dias',
    waitingMinutes: 118,
    score: 52,
    lastMessage: 'Vou pensar no orcamento que mandou',
    classification: 'OPPORTUNITY'
  },
  {
    id: '3',
    remoteJid: '5511444444444@s.whatsapp.net',
    contactName: 'Julia Lima',
    waitingMinutes: 83,
    score: 38,
    lastMessage: 'Quando fica pronto o servico?',
    classification: 'FOLLOW_UP'
  }
];

// Utility functions
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

const formatTime = (minutes: number): string => {
  if (minutes < 60) return `${minutes}min`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}min`;
};

const getScoreColor = (score: number): string => {
  if (score >= 80) return 'text-red-600 bg-red-100';
  if (score >= 50) return 'text-orange-600 bg-orange-100';
  if (score >= 30) return 'text-yellow-600 bg-yellow-100';
  return 'text-green-600 bg-green-100';
};

// Section 1: Header + Metrics
const DashboardHeader: React.FC<{ mode: string; metrics: Metrics }> = ({ mode, metrics }) => {
  const currentDate = new Date().toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });

  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'STEALTH': return '🔇';
      case 'ACTIVE': return '📢';
      case 'HYBRID': return '🎯';
      default: return '⚙️';
    }
  };

  return (
    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 rounded-lg shadow-lg mb-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-bold">SDR Virtual - Painel de Controle</h1>
          <p className="text-indigo-200">
            {getModeIcon(mode)} Modo: {mode} | ✅ Online | {currentDate}
          </p>
        </div>
        <div className="text-right">
          <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
            Horario Comercial
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          icon="📬"
          value={metrics.messagesReceived.toString()}
          label="Mensagens"
          change="+23 vs ontem"
          positive={true}
        />
        <MetricCard
          icon="🔥"
          value={metrics.hotLeads.toString()}
          label="Hot Leads"
          change="+3 vs ontem"
          positive={true}
        />
        <MetricCard
          icon="⏱️"
          value={`${metrics.avgResponseTime}min`}
          label="Tempo Medio"
          change="-5min"
          positive={true}
        />
        <MetricCard
          icon="💰"
          value={formatCurrency(metrics.revenue)}
          label="Vendas Dia"
          change="+12%"
          positive={true}
        />
      </div>
    </div>
  );
};

const MetricCard: React.FC<{
  icon: string;
  value: string;
  label: string;
  change: string;
  positive: boolean;
}> = ({ icon, value, label, change, positive }) => (
  <div className="bg-white/10 backdrop-blur rounded-lg p-4">
    <div className="flex items-center gap-2 mb-2">
      <span className="text-2xl">{icon}</span>
      <span className="text-2xl font-bold">{value}</span>
    </div>
    <p className="text-sm text-indigo-200">{label}</p>
    <p className={`text-xs ${positive ? 'text-green-300' : 'text-red-300'}`}>
      {change}
    </p>
  </div>
);

// Section 2: Hot Leads
const HotLeadsSection: React.FC<{ leads: Lead[] }> = ({ leads }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          🔥 Hot Leads - Acao Imediata
        </h2>
        <span className="text-sm text-gray-500">{leads.length} leads</span>
      </div>

      <div className="space-y-4">
        {leads.map((lead, index) => (
          <LeadCard key={lead.id} lead={lead} index={index + 1} />
        ))}
      </div>
    </div>
  );
};

const LeadCard: React.FC<{ lead: Lead; index: number }> = ({ lead, index }) => {
  const isUrgent = lead.waitingMinutes > 5 && lead.score >= 80;

  return (
    <div className={`border rounded-lg p-4 ${isUrgent ? 'border-red-300 bg-red-50' : 'border-gray-200'}`}>
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-bold text-gray-800">{index}. {lead.contactName}</span>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getScoreColor(lead.score)}`}>
              {lead.score} pts
            </span>
            {isUrgent && <span className="text-red-500 text-sm">⚠️ SLA</span>}
          </div>
          <p className="text-gray-600 text-sm mb-2">"{lead.lastMessage}"</p>
          <div className="flex gap-4 text-xs text-gray-500">
            <span>⏱️ {formatTime(lead.waitingMinutes)}</span>
            <span>🎯 {lead.intent}</span>
            <span>💰 {formatCurrency(lead.estimatedValue)}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button className="px-3 py-1 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
            💬 Responder
          </button>
          <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">
            📋 Historico
          </button>
        </div>
      </div>
    </div>
  );
};

// Section 3: Forgotten Chats
const ForgottenChatsSection: React.FC<{ chats: ForgottenChat[] }> = ({ chats }) => {
  const criticalCount = chats.filter(c => c.waitingMinutes > 120).length;
  const warningCount = chats.filter(c => c.waitingMinutes <= 120).length;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          ⏰ Esquecidos - Sem Resposta &gt; 1 Hora
        </h2>
        <div className="flex gap-2">
          <span className="px-2 py-1 bg-red-100 text-red-600 rounded text-sm">
            {criticalCount} criticos
          </span>
          <span className="px-2 py-1 bg-yellow-100 text-yellow-600 rounded text-sm">
            {warningCount} alertas
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-3 text-sm font-medium text-gray-600">Nome</th>
              <th className="text-left p-3 text-sm font-medium text-gray-600">Tempo</th>
              <th className="text-left p-3 text-sm font-medium text-gray-600">Score</th>
              <th className="text-left p-3 text-sm font-medium text-gray-600">Ultima Mensagem</th>
              <th className="text-left p-3 text-sm font-medium text-gray-600">Acao</th>
            </tr>
          </thead>
          <tbody>
            {chats.map((chat) => (
              <ForgottenChatRow key={chat.id} chat={chat} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ForgottenChatRow: React.FC<{ chat: ForgottenChat }> = ({ chat }) => {
  const isCritical = chat.waitingMinutes > 120;

  return (
    <tr className={`border-b ${isCritical ? 'bg-red-50' : ''}`}>
      <td className="p-3">
        <div className="font-medium text-gray-800">{chat.contactName}</div>
        <div className="text-xs text-gray-500">{chat.classification}</div>
      </td>
      <td className="p-3">
        <span className={`font-medium ${isCritical ? 'text-red-600' : 'text-yellow-600'}`}>
          {formatTime(chat.waitingMinutes)}
        </span>
      </td>
      <td className="p-3">
        <span className={`px-2 py-0.5 rounded text-xs ${getScoreColor(chat.score)}`}>
          {chat.score}
        </span>
      </td>
      <td className="p-3 text-sm text-gray-600 max-w-xs truncate">
        {chat.lastMessage}
      </td>
      <td className="p-3">
        <button className="px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700">
          💬
        </button>
      </td>
    </tr>
  );
};

// Section 4: Analytics Charts
const AnalyticsSection: React.FC<{ metrics: Metrics }> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      {/* Pipeline Chart */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">📊 Pipeline de Vendas</h3>
        <div className="space-y-3">
          <PipelineBar label="LEAD" value={23} max={50} color="bg-blue-500" amount={null} />
          <PipelineBar label="MQL" value={12} max={50} color="bg-green-500" amount={null} />
          <PipelineBar label="SQL" value={8} max={50} color="bg-yellow-500" amount={45000} />
          <PipelineBar label="OPPORTUNITY" value={5} max={50} color="bg-orange-500" amount={38000} />
          <PipelineBar label="PROPOSAL" value={3} max={50} color="bg-red-500" amount={42000} />
        </div>
        <div className="mt-4 pt-4 border-t">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Pipeline Total:</span>
            <span className="font-bold text-gray-800">{formatCurrency(125000)}</span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-gray-600">Taxa de Conversao:</span>
            <span className="font-bold text-green-600">31.8%</span>
          </div>
        </div>
      </div>

      {/* SLA Chart */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">⏱️ Performance de SLA</h3>
        <div className="flex items-center justify-center mb-4">
          <div className="relative w-32 h-32">
            <svg className="w-full h-full" viewBox="0 0 100 100">
              <circle
                className="text-gray-200"
                strokeWidth="10"
                stroke="currentColor"
                fill="transparent"
                r="40"
                cx="50"
                cy="50"
              />
              <circle
                className="text-indigo-600"
                strokeWidth="10"
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="40"
                cx="50"
                cy="50"
                strokeDasharray={`${metrics.slaRate * 2.51} 251`}
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold text-gray-800">{metrics.slaRate}%</span>
            </div>
          </div>
        </div>
        <div className="text-center text-sm text-gray-600">
          Meta: 95% | Status: {metrics.slaRate >= 95 ? '✅' : '⚠️'}
        </div>
        <div className="mt-4 space-y-2">
          <SLABar label="Hot Leads" value={85} target={95} />
          <SLABar label="Oportunidades" value={78} target={90} />
          <SLABar label="Follow-ups" value={92} target={85} />
        </div>
      </div>

      {/* Sentiment Chart */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">💭 Analise de Sentimento</h3>
        <div className="space-y-2">
          <SentimentBar emoji="😊" label="Muito Positivo" value={15} color="bg-green-500" />
          <SentimentBar emoji="🙂" label="Positivo" value={46} color="bg-green-400" />
          <SentimentBar emoji="😐" label="Neutro" value={27} color="bg-gray-400" />
          <SentimentBar emoji="😕" label="Negativo" value={9} color="bg-orange-400" />
          <SentimentBar emoji="😡" label="Muito Negativo" value={3} color="bg-red-500" />
        </div>
        <div className="mt-4 pt-4 border-t text-sm text-gray-600">
          Tendencia: <span className="font-medium text-gray-800">Estavel</span>
        </div>
      </div>

      {/* Messages by Hour */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">📈 Mensagens por Hora</h3>
        <div className="flex items-end justify-between h-32 gap-1">
          {[5, 12, 28, 45, 38, 52, 35, 22, 15, 8].map((value, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div
                className="w-full bg-indigo-500 rounded-t"
                style={{ height: `${(value / 52) * 100}%` }}
              />
              <span className="text-xs text-gray-500 mt-1">{8 + index}h</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const PipelineBar: React.FC<{
  label: string;
  value: number;
  max: number;
  color: string;
  amount: number | null;
}> = ({ label, value, max, color, amount }) => (
  <div className="flex items-center gap-2">
    <span className="w-24 text-sm text-gray-600">{label}</span>
    <div className="flex-1 bg-gray-100 rounded h-4">
      <div
        className={`${color} h-full rounded`}
        style={{ width: `${(value / max) * 100}%` }}
      />
    </div>
    <span className="w-8 text-sm text-gray-800 font-medium">{value}</span>
    {amount && (
      <span className="w-24 text-sm text-gray-600 text-right">
        {formatCurrency(amount)}
      </span>
    )}
  </div>
);

const SLABar: React.FC<{ label: string; value: number; target: number }> = ({
  label,
  value,
  target
}) => (
  <div className="flex items-center gap-2 text-sm">
    <span className="w-24 text-gray-600">{label}</span>
    <div className="flex-1 bg-gray-100 rounded h-2">
      <div
        className={`h-full rounded ${value >= target ? 'bg-green-500' : 'bg-yellow-500'}`}
        style={{ width: `${value}%` }}
      />
    </div>
    <span className={value >= target ? 'text-green-600' : 'text-yellow-600'}>
      {value}%
    </span>
  </div>
);

const SentimentBar: React.FC<{
  emoji: string;
  label: string;
  value: number;
  color: string;
}> = ({ emoji, label, value, color }) => (
  <div className="flex items-center gap-2">
    <span className="w-6">{emoji}</span>
    <span className="w-28 text-sm text-gray-600">{label}</span>
    <div className="flex-1 bg-gray-100 rounded h-3">
      <div className={`${color} h-full rounded`} style={{ width: `${value}%` }} />
    </div>
    <span className="w-10 text-sm text-gray-800 text-right">{value}%</span>
  </div>
);

// Section 5: Action Center
const ActionCenterSection: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">🎯 Acoes Rapidas</h2>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <ActionButton icon="📊" label="Relatorio" command="/wa-relatorio" />
        <ActionButton icon="🔄" label="Sincronizar" command="HubSpot Sync" />
        <ActionButton icon="⚙️" label="Configurar" command="/wa-mode" />
        <ActionButton icon="🛡️" label="Ver Spam" command="/wa-spam" />
        <ActionButton icon="📋" label="Pipeline" command="/wa-leads" />
        <ActionButton icon="📅" label="Agenda" command="Google Calendar" />
      </div>

      <div className="border-t pt-4">
        <h3 className="font-medium text-gray-800 mb-3">⚡ Proximas Acoes Recomendadas</h3>
        <div className="space-y-2">
          <RecommendedAction
            priority="URGENTE"
            text="Responder Pedro Costa (hot lead 15min)"
            color="bg-red-100 text-red-700"
          />
          <RecommendedAction
            priority="FOLLOW-UP"
            text="3 propostas pendentes ha 48h"
            color="bg-yellow-100 text-yellow-700"
          />
          <RecommendedAction
            priority="RECUPERAR"
            text="5 conversas esquecidas"
            color="bg-orange-100 text-orange-700"
          />
          <RecommendedAction
            priority="CELEBRAR"
            text="7 vendas fechadas hoje! 🎉"
            color="bg-green-100 text-green-700"
          />
        </div>
      </div>
    </div>
  );
};

const ActionButton: React.FC<{ icon: string; label: string; command: string }> = ({
  icon,
  label,
  command
}) => (
  <button className="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors">
    <span className="text-2xl mb-1">{icon}</span>
    <span className="text-sm font-medium text-gray-800">{label}</span>
    <span className="text-xs text-gray-500">{command}</span>
  </button>
);

const RecommendedAction: React.FC<{
  priority: string;
  text: string;
  color: string;
}> = ({ priority, text, color }) => (
  <div className="flex items-center gap-3">
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {priority}
    </span>
    <span className="text-sm text-gray-700">{text}</span>
  </div>
);

// Main Dashboard Component
const SDRDashboard: React.FC = () => {
  const [mode, setMode] = useState<string>('HYBRID');
  const [metrics, setMetrics] = useState<Metrics>(mockMetrics);
  const [hotLeads, setHotLeads] = useState<Lead[]>(mockHotLeads);
  const [forgottenChats, setForgottenChats] = useState<ForgottenChat[]>(mockForgottenChats);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      // In production, this would fetch real data from the MCP
      console.log('Refreshing dashboard data...');
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <DashboardHeader mode={mode} metrics={metrics} />
        <HotLeadsSection leads={hotLeads} />
        <ForgottenChatsSection chats={forgottenChats} />
        <AnalyticsSection metrics={metrics} />
        <ActionCenterSection />

        {/* Footer */}
        <div className="text-center text-sm text-gray-500 mt-6">
          <p>SDR Virtual - Evolution WhatsApp Business</p>
          <p>Ultima atualizacao: {new Date().toLocaleTimeString('pt-BR')}</p>
        </div>
      </div>
    </div>
  );
};

export default SDRDashboard;
