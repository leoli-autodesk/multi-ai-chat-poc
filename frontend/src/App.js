// 私校申请顾问AI协作系统 - 主应用组件
const { useState, useEffect, useRef } = React;

// 类型定义
const MessageType = {
    ADMISSIONS_OFFICER: 'Admissions Officer',
    PARENT: 'Parent',
    STUDENT: 'Student',
    ADVISOR: 'Advisor',
    WRITER: 'Writer',
    SYSTEM: 'System'
};

const MessageRole = {
    ADMISSIONS_OFFICER: 'admissions_officer',
    PARENT: 'parent',
    STUDENT: 'student',
    ADVISOR: 'advisor',
    WRITER: 'writer'
};

// 主应用组件
function App() {
    const [currentStep, setCurrentStep] = useState('form'); // form, conversation, report
    const [formData, setFormData] = useState({});
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState(null);
    const [report, setReport] = useState('');
    
    // 处理表单提交
    const handleFormSubmit = async (data) => {
        setFormData(data);
        setIsLoading(true);
        
        try {
            // 调用后端API开始对话
            const response = await fetch('/api/start-conversation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            setConversationId(result.conversationId);
            setCurrentStep('conversation');
            
            // 开始第一轮对话
            await startConversation(result.conversationId);
            
        } catch (error) {
            console.error('启动对话失败:', error);
            alert('启动对话失败，请重试');
        } finally {
            setIsLoading(false);
        }
    };
    
    // 开始对话
    const startConversation = async (convId) => {
        try {
            const response = await fetch(`/api/conversation/${convId}/start`, {
                method: 'POST'
            });
            
            const result = await response.json();
            setMessages(result.messages || []);
            
            // 开始对话循环
            await runConversationLoop(convId);
            
        } catch (error) {
            console.error('对话启动失败:', error);
        }
    };
    
    // 运行对话循环
    const runConversationLoop = async (convId) => {
        try {
            const response = await fetch(`/api/conversation/${convId}/run`, {
                method: 'POST'
            });
            
            const result = await response.json();
            setMessages(result.messages || []);
            
            // 如果对话结束，显示报告
            if (result.status === 'completed') {
                setReport(result.report);
                setCurrentStep('report');
            }
            
        } catch (error) {
            console.error('对话运行失败:', error);
        }
    };
    
    // 渲染当前步骤
    const renderCurrentStep = () => {
        switch (currentStep) {
            case 'form':
                return <InputForm onSubmit={handleFormSubmit} isLoading={isLoading} />;
            case 'conversation':
                return <ConversationInterface messages={messages} isLoading={isLoading} />;
            case 'report':
                return <ReportViewer report={report} formData={formData} />;
            default:
                return <InputForm onSubmit={handleFormSubmit} isLoading={isLoading} />;
        }
    };
    
    return (
        <div className="min-h-screen bg-gray-50">
            {/* 头部导航 */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-4">
                        <div className="flex items-center">
                            <h1 className="text-2xl font-bold text-gray-900">
                                私校申请顾问AI协作系统
                            </h1>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm text-gray-500">
                                {currentStep === 'form' && '输入信息'}
                                {currentStep === 'conversation' && 'AI对话中'}
                                {currentStep === 'report' && '查看报告'}
                            </span>
                        </div>
                    </div>
                </div>
            </header>
            
            {/* 主内容区域 */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {renderCurrentStep()}
            </main>
        </div>
    );
}

// 输入表单组件
function InputForm({ onSubmit, isLoading }) {
    const [formData, setFormData] = useState({
        studentName: '',
        age: '',
        currentGrade: '',
        targetGrade: '',
        nationality: '',
        familyStructure: '',
        parentOccupation: '',
        educationPhilosophy: '',
        currentSchool: '',
        academicPerformance: '',
        strongSubjects: '',
        weakSubjects: '',
        englishLevel: '',
        frenchLevel: '',
        standardizedTests: '',
        sports: '',
        arts: '',
        academicCompetitions: '',
        leadership: '',
        communityService: '',
        achievements: '',
        personality: '',
        strengths: '',
        improvements: '',
        studyHabits: '',
        socialSkills: '',
        independence: '',
        stressManagement: '',
        culturalAdaptation: '',
        targetSchool1: '',
        targetSchool2: '',
        targetSchool3: '',
        schoolSelectionReason: '',
        schoolPreferences: '',
        applicationDeadline: '',
        ssatTestDate: '',
        interviewDate: '',
        otherDates: '',
        learningSupport: '',
        accommodation: '',
        transportation: '',
        budget: '',
        concerns: '',
        expectations: ''
    });
    
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };
    
    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };
    
    const fillSampleData = () => {
        setFormData({
            studentName: 'Alex Chen',
            age: '14',
            currentGrade: 'Grade 8',
            targetGrade: 'Grade 9',
            nationality: '中国公民，持有学习签证',
            familyStructure: '三口之家，父母都是工程师',
            parentOccupation: '父亲是软件工程师，母亲是建筑工程师',
            educationPhilosophy: '重视全面发展，支持孩子探索兴趣',
            currentSchool: '国际学校',
            academicPerformance: 'GPA 3.8/4.0',
            strongSubjects: '数学、物理、计算机科学',
            weakSubjects: '英语文学、历史',
            englishLevel: 'Advanced（IELTS 7.0）',
            frenchLevel: '基础水平',
            standardizedTests: 'SSAT 85th percentile',
            sports: '篮球、游泳',
            arts: '钢琴（RCM Grade 6）',
            academicCompetitions: '数学竞赛省级二等奖',
            leadership: '学生会科技部副部长',
            communityService: '社区环保活动组织者，累计义工50小时',
            achievements: '机器人竞赛省级二等奖',
            personality: '内向但专注，逻辑思维强',
            strengths: '专注力强、逻辑清晰、有责任心',
            improvements: '表达能力、社交技巧',
            studyHabits: '喜欢独立思考和解决问题',
            socialSkills: '在小群体中表现良好',
            independence: '较强，能够独立完成学习任务',
            stressManagement: '良好，能够应对学术压力',
            culturalAdaptation: '较强，能够适应多元文化环境',
            targetSchool1: 'Upper Canada College',
            targetSchool2: 'Havergal College',
            targetSchool3: 'St. Andrew\'s College',
            schoolSelectionReason: '学术氛围浓厚，STEM教育强，国际化程度高',
            schoolPreferences: '学术挑战性、STEM项目、领导力培养',
            applicationDeadline: '2024年12月31日',
            ssatTestDate: '2024年11月15日',
            interviewDate: '2025年1月15日',
            otherDates: '材料提交2024年12月20日',
            learningSupport: '无特殊需求',
            accommodation: '走读',
            transportation: '父母接送',
            budget: '年学费预算$50,000-60,000',
            concerns: '希望学校有良好的STEM项目和大学升学指导',
            expectations: '获得优质教育，为未来STEM发展和大学申请打基础'
        });
    };
    
    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">家长访谈信息</h2>
                <button
                    type="button"
                    onClick={fillSampleData}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                    填充示例数据
                </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
                {/* 基本信息 */}
                <div className="border-b pb-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">基本信息</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                学生姓名
                            </label>
                            <input
                                type="text"
                                name="studentName"
                                value={formData.studentName}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                年龄
                            </label>
                            <input
                                type="text"
                                name="age"
                                value={formData.age}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                当前年级
                            </label>
                            <input
                                type="text"
                                name="currentGrade"
                                value={formData.currentGrade}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                目标申请年级
                            </label>
                            <input
                                type="text"
                                name="targetGrade"
                                value={formData.targetGrade}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>
                    </div>
                </div>
                
                {/* 目标学校 */}
                <div className="border-b pb-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">目标学校</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                目标学校1
                            </label>
                            <select
                                name="targetSchool1"
                                value={formData.targetSchool1}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            >
                                <option value="">请选择</option>
                                <option value="Upper Canada College">Upper Canada College</option>
                                <option value="Havergal College">Havergal College</option>
                                <option value="St. Andrew's College">St. Andrew's College</option>
                                <option value="Crescent School">Crescent School</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                目标学校2
                            </label>
                            <select
                                name="targetSchool2"
                                value={formData.targetSchool2}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">请选择</option>
                                <option value="Upper Canada College">Upper Canada College</option>
                                <option value="Havergal College">Havergal College</option>
                                <option value="St. Andrew's College">St. Andrew's College</option>
                                <option value="Crescent School">Crescent School</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                目标学校3
                            </label>
                            <select
                                name="targetSchool3"
                                value={formData.targetSchool3}
                                onChange={handleInputChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">请选择</option>
                                <option value="Upper Canada College">Upper Canada College</option>
                                <option value="Havergal College">Havergal College</option>
                                <option value="St. Andrew's College">St. Andrew's College</option>
                                <option value="Crescent School">Crescent School</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                选择原因
                            </label>
                            <textarea
                                name="schoolSelectionReason"
                                value={formData.schoolSelectionReason}
                                onChange={handleInputChange}
                                rows="3"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="请说明选择这些学校的原因..."
                            />
                        </div>
                    </div>
                </div>
                
                {/* 提交按钮 */}
                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {isLoading ? '启动中...' : '开始AI对话'}
                    </button>
                </div>
            </form>
        </div>
    );
}

// 对话界面组件
function ConversationInterface({ messages, isLoading }) {
    const messagesEndRef = useRef(null);
    
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };
    
    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    
    const getRoleColor = (role) => {
        const colors = {
            'Admissions Officer': 'bg-blue-100 text-blue-800',
            'Parent': 'bg-green-100 text-green-800',
            'Student': 'bg-purple-100 text-purple-800',
            'Advisor': 'bg-orange-100 text-orange-800',
            'Writer': 'bg-gray-100 text-gray-800',
            'System': 'bg-yellow-100 text-yellow-800'
        };
        return colors[role] || 'bg-gray-100 text-gray-800';
    };
    
    const formatMessage = (message) => {
        if (typeof message === 'string') {
            return message;
        }
        
        if (typeof message === 'object') {
            return JSON.stringify(message, null, 2);
        }
        
        return String(message);
    };
    
    return (
        <div className="bg-white rounded-lg shadow-lg">
            <div className="p-4 border-b">
                <h2 className="text-xl font-semibold text-gray-900">AI对话进行中</h2>
                <p className="text-sm text-gray-600">多角色AI正在讨论申请策略...</p>
            </div>
            
            <div className="h-96 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, index) => (
                    <div key={index} className="chat-message">
                        <div className="flex items-start space-x-3">
                            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(msg.role)}`}>
                                {msg.role}
                            </div>
                            <div className="flex-1">
                                <div className="bg-gray-50 rounded-lg p-3">
                                    <pre className="whitespace-pre-wrap text-sm text-gray-800">
                                        {formatMessage(msg.content)}
                                    </pre>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
                
                {isLoading && (
                    <div className="flex items-center space-x-3">
                        <div className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            System
                        </div>
                        <div className="flex-1">
                            <div className="bg-gray-50 rounded-lg p-3">
                                <div className="flex items-center space-x-2">
                                    <div className="typing-indicator w-2 h-2 bg-gray-400 rounded-full"></div>
                                    <div className="typing-indicator w-2 h-2 bg-gray-400 rounded-full" style={{animationDelay: '0.2s'}}></div>
                                    <div className="typing-indicator w-2 h-2 bg-gray-400 rounded-full" style={{animationDelay: '0.4s'}}></div>
                                    <span className="text-sm text-gray-600 ml-2">AI正在思考...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>
        </div>
    );
}

// 报告查看器组件
function ReportViewer({ report, formData }) {
    const downloadReport = () => {
        const element = document.createElement('a');
        const file = new Blob([report], { type: 'text/markdown' });
        element.href = URL.createObjectURL(file);
        element.download = `申请策略报告_${formData.studentName}_${new Date().toISOString().split('T')[0]}.md`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };
    
    return (
        <div className="bg-white rounded-lg shadow-lg">
            <div className="p-4 border-b flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">申请策略报告</h2>
                <button
                    onClick={downloadReport}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                >
                    下载报告
                </button>
            </div>
            
            <div className="p-6">
                <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed">
                        {report}
                    </pre>
                </div>
            </div>
        </div>
    );
}

// 渲染应用
ReactDOM.render(<App />, document.getElementById('root'));
