#!/usr/bin/env python3
import os
import time
import threading
from hypocrisy_detector import HypocrisyDetector
from news_monitor import create_breaking_news
import json

class HypocrisyDemo:
    def __init__(self):
        self.detector = HypocrisyDetector()
        self.running = False

    def setup_demo(self):
        """Setup demo environment"""
        print("🚀 Setting up AI Corporate Hypocrisy Detector Demo...")
        print("=" * 60)

        # Setup demo data
        self.detector.setup_demo_data()

        # Start news monitoring
        self.detector.news_monitor.start_monitoring()

        print("✅ Demo setup complete!\n")

    def show_banner(self):
        """Display demo banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║           AI CORPORATE HYPOCRISY DETECTOR                    ║
║                   Live Demo System                           ║
║                                                              ║
║  Real-time analysis of corporate promises vs actions        ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def analyze_company_interactive(self):
        """Interactive company analysis"""
        print("\n📊 Company Analysis Mode")
        print("-" * 40)

        while True:
            print("\nAvailable companies: TechCorp")
            company = input("Enter company name (or 'back' to return): ").strip()

            if company.lower() == 'back':
                break

            if not company:
                continue

            print(f"\nAnalyzing {company}...")
            print("You can ask about:")
            print("- Environmental practices")
            print("- Employee treatment")
            print("- Business ethics")
            print("- General corporate behavior")

            query = input("What would you like to analyze? (or press Enter for general): ").strip()

            print(f"\n🔍 Analyzing {company}...")
            result = self.detector.analyze_company(company, query)

            self.display_analysis_result(result)

            input("\nPress Enter to continue...")

    def display_analysis_result(self, result):
        """Display analysis results in a formatted way"""
        print("\n" + "="*60)
        print(f"🏢 ANALYSIS RESULTS: {result.company}")
        print("="*60)

        # Color coding for contradiction levels
        level_colors = {
            'HIGH': '🚨',
            'MEDIUM': '⚠️',
            'LOW': '🟡',
            'NONE': '✅',
            'UNKNOWN': '❓'
        }

        icon = level_colors.get(result.contradiction_level, '❓')
        print(f"{icon} CONTRADICTION LEVEL: {result.contradiction_level}")
        print(f"📊 CONFIDENCE SCORE: {result.confidence_score:.2f}")

        if result.query:
            print(f"🔍 QUERY FOCUS: {result.query}")

        print(f"\n📝 ANALYSIS:")
        print(result.analysis)

        print(f"\n📋 COMPANY PROMISES (excerpt):")
        print(result.promises_excerpt)

        print(f"\n📰 RECENT ACTIONS (excerpt):")
        print(result.actions_excerpt)

        print("="*60)

    def live_monitoring_demo(self):
        """Demonstrate live monitoring capabilities"""
        print("\n📡 Live Monitoring Demo")
        print("-" * 40)
        print("This mode simulates real-time news monitoring.")
        print("Watch how the AI's analysis changes as new information arrives.\n")

        company = "TechCorp"

        # Show baseline analysis
        print("📊 BASELINE ANALYSIS")
        print("-" * 20)
        baseline_result = self.detector.analyze_company(company, "environmental policy")
        self.display_analysis_result(baseline_result)

        input("\n🎬 Press Enter to simulate breaking news arrival...")

        print("\n📰 BREAKING NEWS SIMULATION")
        print("-" * 30)

        # Create breaking news that contradicts the company's environmental commitments
        breaking_news = {
            "headline": "TechCorp Fined $50 Million for Illegal Toxic Waste Dumping",
            "content": "EPA investigators found that TechCorp has been illegally dumping toxic manufacturing waste into local waterways for the past two years, directly violating environmental regulations. The company faces additional criminal charges and potential facility shutdowns. Local communities report significant environmental damage and health concerns.",
            "severity": "HIGH"
        }

        print(f"🚨 {breaking_news['headline']}")
        print(f"📄 {breaking_news['content'][:200]}...")

        # Create the breaking news file
        create_breaking_news(
            company=company,
            headline=breaking_news['headline'],
            content=breaking_news['content'],
            severity=breaking_news['severity']
        )

        print(f"\n⏳ Processing new information... (waiting 3 seconds)")
        time.sleep(3)  # Give time for file processing

        # Show updated analysis
        print("\n📊 UPDATED ANALYSIS")
        print("-" * 20)
        updated_result = self.detector.analyze_company(company, "environmental policy")
        self.display_analysis_result(updated_result)

        print("\n🎯 DEMO IMPACT:")
        print(f"   Before: {baseline_result.contradiction_level} confidence {baseline_result.confidence_score:.2f}")
        print(f"   After:  {updated_result.contradiction_level} confidence {updated_result.confidence_score:.2f}")

        if updated_result.contradiction_level != baseline_result.contradiction_level:
            print("   ✅ AI successfully detected the contradiction!")
        else:
            print("   ℹ️ Analysis updated with new information")

    def batch_analysis_demo(self):
        """Demonstrate batch analysis of multiple topics"""
        print("\n🔄 Batch Analysis Demo")
        print("-" * 40)

        company = "TechCorp"
        topics = [
            "environmental sustainability",
            "employee treatment and diversity",
            "business ethics and transparency",
            "community involvement"
        ]

        print(f"Analyzing {company} across multiple dimensions...\n")

        results = []
        for topic in topics:
            print(f"🔍 Analyzing: {topic}")
            result = self.detector.analyze_company(company, topic)
            results.append(result)
            print(f"   Result: {result.contradiction_level} (confidence: {result.confidence_score:.2f})")

        # Summary
        print(f"\n📊 SUMMARY FOR {company}:")
        print("-" * 30)
        for i, result in enumerate(results):
            icon = {'HIGH': '🚨', 'MEDIUM': '⚠️', 'LOW': '🟡', 'NONE': '✅'}.get(result.contradiction_level, '❓')
            print(f"{icon} {topics[i]}: {result.contradiction_level}")

    def main_menu(self):
        """Main demo menu"""
        while True:
            print("\n🎛️  DEMO MENU")
            print("=" * 40)
            print("1. 🔍 Interactive Company Analysis")
            print("2. 📡 Live Monitoring Demo")
            print("3. 🔄 Batch Analysis Demo")
            print("4. 📰 Create Custom Breaking News")
            print("5. 📊 View Recent News")
            print("6. 🚪 Exit")

            choice = input("\nSelect option (1-6): ").strip()

            if choice == '1':
                self.analyze_company_interactive()
            elif choice == '2':
                self.live_monitoring_demo()
            elif choice == '3':
                self.batch_analysis_demo()
            elif choice == '4':
                self.create_custom_news()
            elif choice == '5':
                self.view_recent_news()
            elif choice == '6':
                break
            else:
                print("❌ Invalid option. Please try again.")

    def create_custom_news(self):
        """Allow user to create custom news for testing"""
        print("\n📝 Create Custom Breaking News")
        print("-" * 40)

        company = input("Company name: ").strip() or "TechCorp"
        headline = input("Headline: ").strip()
        content = input("Content: ").strip()

        if headline and content:
            create_breaking_news(company, headline, content)
            print("✅ Breaking news created and will be processed automatically!")
        else:
            print("❌ Headline and content are required")

    def view_recent_news(self):
        """View recent news items"""
        print("\n📰 Recent News")
        print("-" * 40)

        news_items = self.detector.news_monitor.news_items
        if not news_items:
            print("No news items found")
            return

        for i, item in enumerate(news_items[-5:], 1):  # Show last 5
            print(f"\n{i}. [{item.get('severity', 'UNKNOWN')}] {item.get('company', 'Unknown')}")
            print(f"   📰 {item.get('headline', '')}")
            print(f"   📄 {item.get('content', '')[:100]}...")

    def cleanup(self):
        """Cleanup demo resources"""
        print("\n🧹 Cleaning up...")
        self.detector.news_monitor.stop_monitoring()
        print("✅ Demo cleanup complete")

def main():
    """Main demo function"""
    demo = HypocrisyDemo()

    try:
        demo.show_banner()
        demo.setup_demo()
        demo.main_menu()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()