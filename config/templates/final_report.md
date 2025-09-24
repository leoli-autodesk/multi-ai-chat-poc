# 🎯 私校申请策略报告

## 📋 目录

1. [家庭与学生背景](#家庭与学生背景) (约3页)
2. [学校申请定位](#学校申请定位) (约2页)
3. [学生—学校匹配度](#学生学校匹配度) (约4页)
4. [学术与课外准备](#学术与课外准备) (约3页)
5. [申请流程与个性化策略](#申请流程与个性化策略) (约2.5页)
6. [录取后延伸建议](#录取后延伸建议) (约0.5页)

---

## 📋 学生概况
- **姓名**: {{student_name}}
- **年龄**: {{age}} ({{grade}})
- **目标年级**: Grade 9
- **目标学校**: Upper Canada College, Havergal College, St. Andrew's College

---

## 👨‍👩‍👧‍👦 家庭与学生背景

### 家庭教育理念与价值观
**家庭价值观**: {{family.education_values}}
**教育目标**: {{family.goals}}
**文化背景**: {{family.culture}}
**支持程度**: {{family.support_level}}
**期望设定**: {{family.expectations}}
**资源投入**: {{family.resources}}

### 学业与学习风格
**GPA**: {{gpa}} - {{academic_level}}
**强项领域**: {{academic_strengths}}
**标准化考试**: {{test_scores}}
**学术竞赛**: {{competition_achievements}}
**学习能力**: {{learning_ability}}
**适应能力**: {{adaptability}}

### 个性与社交
**创新思维**: {{innovation_examples}}
**责任感**: {{responsibility_examples}}
**团队协作**: {{teamwork_examples}}
**影响力**: {{impact_metrics}}
**项目经验**: {{project_experiences}}

### 兴趣与特长
**专业特长**: {{professional_expertise}}
**全球视野**: {{global_perspective}}
**创新精神**: {{innovative_spirit}}
**全面发展**: {{holistic_development}}

---

## 🏫 学校申请定位

### 家长择校标准
**核心标准**: {{positioning.parent_criteria}}
**学校类型偏好**: {{positioning.school_type_preference}}
**地理位置偏好**: {{positioning.location_preference}}
**预算范围**: {{positioning.budget_range}}

### 学校资源扫描
{{positioning.resource_scan_summary}}

---

## 🏫 学生—学校匹配度（核心）

### 匹配维度与权重
| 维度 | 权重 | 说明 |
|---|---:|---|
| 学术 | {{matching_analysis.weights.academic}} | {{matching_analysis.scoring_criteria.academic}} |
| 活动资源 | {{matching_analysis.weights.activities}} | {{matching_analysis.scoring_criteria.activities}} |
| 价值观/文化 | {{matching_analysis.weights.culture}} | {{matching_analysis.scoring_criteria.culture}} |
| 性格/氛围 | {{matching_analysis.weights.personality}} | {{matching_analysis.scoring_criteria.personality}} |

> 评分规则：每维度 1–5 分；总分 = Σ(维度分 × 权重) × 20 = **百分制**。

{{#each target_schools}}
#### {{name}} — 综合匹配度：**{{match_percentage}}%**

**基本信息**:
- 学校类型: {{facts.type}}
- 班级规模: {{facts.class_size}}
- 师生比例: {{facts.student_teacher_ratio}}
- 学费范围: {{facts.tuition}}
- 地理位置: {{facts.location}}

**特色项目**:
- {{facts.signature_programs.0}}
- {{facts.signature_programs.1}}
- {{facts.signature_programs.2}}

**维度得分**:
- 学术: {{scores.academic}}/5
- 活动: {{scores.activities}}/5
- 文化: {{scores.culture}}/5
- 性格: {{scores.personality}}/5

**优势匹配**:
- ✅ {{advantages.0}}
- ✅ {{advantages.1}}
- ✅ {{advantages.2}}

**申请建议**:
- 🎯 {{strategies.0}}
- 🎯 {{strategies.1}}
- 🎯 {{strategies.2}}

**潜在挑战**:
- ⚠️ {{challenges.0}}
- ⚠️ {{challenges.1}}

**面试提示**:
{{interview_tips}}

**推荐理由（透明）**: {{rationale}}

---

{{/each}}

### 顾问推荐排序（从高到低）
1) **{{matching_analysis.top_recommendations.top1.name}}**（{{matching_analysis.top_recommendations.top1.match_percentage}}%）— 关键理由：{{matching_analysis.top_recommendations.top1.reason}}
2) **{{matching_analysis.top_recommendations.top2.name}}**（{{matching_analysis.top_recommendations.top2.match_percentage}}%）— 关键理由：{{matching_analysis.top_recommendations.top2.reason}}
3) **{{matching_analysis.top_recommendations.top3.name}}**（{{matching_analysis.top_recommendations.top3.match_percentage}}%）— 关键理由：{{matching_analysis.top_recommendations.top3.reason}}

---

## 📚 学术与课外准备

### 学术补强计划
**数学强化**: {{academic_preparation.subject_strengthening.math}}
**英语提升**: {{academic_preparation.subject_strengthening.english}}
**科学深化**: {{academic_preparation.subject_strengthening.science}}
**社科拓展**: {{academic_preparation.subject_strengthening.social_studies}}

### 语言提升路径
**阅读能力**: {{academic_preparation.language_improvement.reading}}
**写作技巧**: {{academic_preparation.language_improvement.writing}}
**口语表达**: {{academic_preparation.language_improvement.speaking}}
**听力理解**: {{academic_preparation.language_improvement.listening}}

### 课外/竞赛/作品集规划
**竞赛参与**: 
- {{extracurricular_preparation.competitions.0}}
- {{extracurricular_preparation.competitions.1}}
- {{extracurricular_preparation.competitions.2}}

**作品集项目**:
- {{extracurricular_preparation.portfolio_projects.0}}
- {{extracurricular_preparation.portfolio_projects.1}}
- {{extracurricular_preparation.portfolio_projects.2}}

### 义工与社区服务
**志愿服务**: 
- {{extracurricular_preparation.volunteer_work.0}}
- {{extracurricular_preparation.volunteer_work.1}}
- {{extracurricular_preparation.volunteer_work.2}}

**社区服务**: {{extracurricular_preparation.community_service}}
**领导力发展**: {{extracurricular_preparation.leadership_development}}

---

## 📅 申请流程与个性化策略

### 流程对比表 + 时间线
**申请阶段**:
- 第一阶段: {{timeline.application_phases.phase_1}}
- 第二阶段: {{timeline.application_phases.phase_2}}
- 第三阶段: {{timeline.application_phases.phase_3}}

**关键截止日期**:
- {{timeline.deadlines.0}}
- {{timeline.deadlines.1}}
- {{timeline.deadlines.2}}

**重要里程碑**:
- {{timeline.milestones.0}}
- {{timeline.milestones.1}}
- {{timeline.milestones.2}}

### 测试准备
**SSAT准备**: {{academic_preparation.test_preparation.ssat}}
**ISEE准备**: {{academic_preparation.test_preparation.isee}}
**校测准备**: {{academic_preparation.test_preparation.school_tests}}

### 推荐信与 Essay 策略
**推荐信策略**: {{application_strategy.recommendation_strategy}}
**Essay主题**:
- {{application_strategy.essay_themes.0}}
- {{application_strategy.essay_themes.1}}
- {{application_strategy.essay_themes.2}}

### 面试辅导
**学生面试**: {{application_strategy.interview_preparation.student_interview}}
**家长面试**: {{application_strategy.interview_preparation.parent_interview}}
**模拟面试**: {{application_strategy.interview_preparation.mock_interviews}}

---

## 🎯 申请策略建议

### 1. 学术提升计划
**目标**: 全面提升学术竞争力
- ✅ **保持优势**: {{maintain_strengths}}
- 📈 **提升空间**: {{improvement_areas}}
- 🎯 **考试准备**: {{test_preparation}}
- 📚 **学习规划**: {{study_plan}}

### 2. 领导力发展路径
**目标**: 展现卓越的领导潜质
- 🚀 **深化现有**: {{deepen_existing}}
- 🌟 **创新项目**: {{innovative_projects}}
- 🤝 **合作能力**: {{collaboration_skills}}
- 📊 **量化成果**: {{quantify_results}}

### 3. 社区影响力建设
**目标**: 建立持续的社区贡献
- 🌱 **扩大影响**: {{expand_influence}}
- ⏰ **长期项目**: {{long_term_projects}}
- 📈 **成果记录**: {{record_results}}
- 🏅 **获得认可**: {{gain_recognition}}

### 4. 个人品牌塑造
**目标**: 展现独特的个人特色
- 🔬 **专业特长**: {{professional_expertise}}
- 🌍 **全球视野**: {{global_perspective}}
- 💡 **创新精神**: {{innovative_spirit}}
- 🎨 **全面发展**: {{holistic_development}}

---

## 📅 行动计划

### 🚀 短期目标 (3个月内)
{{#each plans.short_term_goals}}
{{index}}. **{{category}}**: {{description}}
   - 负责人: {{owner}}
   - 截止日期: {{due_date}}
   - 完成证据: {{evidence}}

{{/each}}

### 🎯 中期目标 (6个月内)
{{#each plans.medium_term_goals}}
{{index}}. **{{category}}**: {{description}}
   - 负责人: {{owner}}
   - 截止日期: {{due_date}}
   - 完成证据: {{evidence}}

{{/each}}

### 🌟 长期目标 (1年内)
{{#each plans.long_term_goals}}
{{index}}. **{{category}}**: {{description}}
   - 负责人: {{owner}}
   - 截止日期: {{due_date}}
   - 完成证据: {{evidence}}

{{/each}}

---

## 💡 专业建议

### 申请策略
- **差异化定位**: {{differentiation_strategy}}
- **故事化表达**: {{storytelling_approach}}
- **量化成果**: {{quantification_method}}
- **未来愿景**: {{future_vision}}

### 风险控制
- **备选方案**: {{risks.backup_plans.0}}, {{risks.backup_plans.1}}, {{risks.backup_plans.2}}
- **时间管理**: {{risks.time_management}}
- **材料准备**: {{risks.material_preparation}}
- **面试准备**: {{risks.interview_preparation}}

### 风险缓解策略
- {{risks.mitigation_strategies.0}}
- {{risks.mitigation_strategies.1}}
- {{risks.mitigation_strategies.2}}

---

## 🎓 录取后延伸建议

### Offer 对比与选择
{{post_admission.offer_comparison}}

### 入学前衔接与心理适应
{{post_admission.transition_preparation}}

### 长远发展（IB/AP/竞赛路线）
{{post_admission.long_term_development}}

---

## 🎉 成功展望

### 我们的专业价值
通过我们的专业指导，{{student_name}}将在申请过程中展现最佳状态：

1. **专业评估**: 全面分析学生优势和潜力
2. **策略制定**: 制定个性化的申请策略
3. **材料优化**: 优化申请材料和文书
4. **面试指导**: 提供专业的面试指导
5. **持续支持**: 全程跟踪和支持申请过程

### 成功保障
- ✅ **经验丰富**: 多年私校申请成功经验
- ✅ **专业团队**: 资深顾问和专家团队
- ✅ **成功案例**: 大量成功录取案例
- ✅ **全程服务**: 从评估到录取的全程服务

### 预期结果
基于{{student_name}}的优秀基础和我们的专业指导，**我们有信心帮助{{student_name}}获得理想学校的录取**。

**让您的孩子看到希望，让我们的专业成就您的梦想！**

---

*报告生成时间: {{report_date}}*  
*专业顾问: {{consultant}}*  
*报告版本: {{report_meta.version}}*  
*页数统计: {{report_meta.page_count}}页*  
*字数统计: {{report_meta.word_count}}字*
