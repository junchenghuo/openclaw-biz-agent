const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, TableWidthType, BorderStyle, WidthType, ShadingType, VerticalAlign } = require('docx');
const fs = require('fs');

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 44, bold: true, color: "000000" },
        paragraph: { spacing: { before: 400, after: 300 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "000000" },
        paragraph: { spacing: { before: 300, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "333333" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Normal", name: "Normal", basedOn: "Normal",
        run: { size: 22, color: "000000" },
        paragraph: { spacing: { after: 120 } } }
    ]
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      // 标题
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("群流程回归-世界时钟-20260315-01")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("产品需求说明书（PRD）", { italics: true, color: "666666" })] }),
      
      // 1. 项目概述
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. 项目概述")] }),
      new Paragraph({ children: [new TextRun("项目名称：群流程回归-世界时钟-20260315-01")] }),
      new Paragraph({ children: [new TextRun("项目目标：展示8国时钟，支持实时时间显示与时区查询")] }),
      new Paragraph({ children: [new TextRun("项目范围：前端 + 后端 + 测试 + 部署")] }),
      new Paragraph({ children: [new TextRun("验收标准：8国时区可查询且误差<1秒")] }),
      
      // 2. 目标用户
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. 目标用户")] }),
      new Paragraph({ children: [new TextRun("• 需要跨时区协作的团队成员"] }),
      new Paragraph({ children: [new TextRun("• 关注全球时区的个人用户")] }),
      
      // 3. 功能需求
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. 功能需求")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 时钟展示"] }),
      new Paragraph({ children: [new TextRun("• 展示8个国家的当前时间（建议：中国、美国、英国、日本、德国、澳大利亚、法国、俄罗斯）")] }),
      new Paragraph({ children: [new TextRun("• 时间自动实时更新，误差<1秒")] }),
      new Paragraph({ children: [new TextRun("• 显示各国时区名称和UTC偏移量")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 时区查询"] }),
      new Paragraph({ children: [new TextRun("• 用户可选择特定国家/时区查看详情"] }),
      new Paragraph({ children: [new TextRun("• 支持时间换算功能"] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 界面交互"] }),
      new Paragraph({ children: [new TextRun("• 清晰的时钟卡片布局"] }),
      new Paragraph({ children: [new TextRun("• 响应式设计，支持移动端和桌面端")] }),
      
      // 4. 非功能需求
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. 非功能需求")] }),
      new Paragraph({ children: [new TextRun("• 性能：页面加载时间<2秒"] }),
      new Paragraph({ children: [new TextRun("• 准确性：时间误差<1秒"] }),
      new Paragraph({ children: [new TextRun("• 可用性：支持主流浏览器（Chrome、Firefox、Safari、Edge）"] }),
      new Paragraph({ children: [new TextRun("• 可访问性：支持基本的屏幕阅读器"] }),
      
      // 5. 技术架构
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. 技术架构"] }),
      new Paragraph({ children: [new TextRun("• 前端：Web技术实现响应式界面"] }),
      new Paragraph({ children: [new TextRun("• 后端：提供标准时间API接口"] }),
      new Paragraph({ children: [new TextRun("• 部署：支持容器化部署"] }),
      
      // 6. 验收标准
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. 验收标准"] }),
      new Paragraph({ children: [new TextRun("✓ 成功展示8个国家的实时时钟")] }),
      new Paragraph({ children: [new TextRun("✓ 时间误差控制在1秒以内")] }),
      new Paragraph({ children: [new TextRun("✓ 界面在移动端和桌面端均正常显示")] }),
      new Paragraph({ children: [new TextRun("✓ 支持至少一种时区查询/换算功能")] }),
      new Paragraph({ children: [new TextRun("✓ 完成部署并可公网访问")] }),
      
      // 7. 里程碑
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. 里程碑"] }),
      new Paragraph({ children: [new TextRun("• M1：PRD + 原型图评审通过（Day 1）"] }),
      new Paragraph({ children: [new TextRun("• M2：架构设计完成（Day 2）"] }),
      new Paragraph({ children: [new TextRun("• M3：开发完成 + 联调通过（Day 4）"] }),
      new Paragraph({ children: [new TextRun("• M4：测试通过 + 部署上线（Day 5）"] }),
      
      // 8. 风险与依赖
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. 风险与依赖") }),
      new Paragraph({ children: [new TextRun("• 风险：时间同步API的稳定性"] }),
      new Paragraph({ children: [new TextRun("• 依赖：后端时间服务接口"] })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/Users/imac/midCreate/openclaw-workspaces/ai-team/projects/世界时钟-20260315-01/deliverables/product/世界时钟-20260315-01-产品需求说明书.doc", buffer);
  console.log("PRD created successfully!");
});
