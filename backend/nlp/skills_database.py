"""
Skills Database - Comprehensive list of tech and soft skills for extraction
"""

TECH_SKILLS = [
    # Programming Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", "Go", "Rust",
    "Swift", "Kotlin", "PHP", "Ruby", "Scala", "R", "MATLAB", "Perl", "Shell",
    "Bash", "PowerShell", "Dart", "Lua", "Haskell", "Elixir", "Clojure",

    # Web Frameworks
    "React", "Next.js", "Vue.js", "Angular", "Svelte", "Nuxt.js", "Remix",
    "FastAPI", "Django", "Flask", "Express.js", "NestJS", "Spring Boot",
    "Laravel", "Rails", "ASP.NET", "Gin", "Echo", "Fiber",

    # Databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle", "SQL Server",
    "Cassandra", "DynamoDB", "Elasticsearch", "Firebase", "Supabase", "Neo4j",
    "InfluxDB", "CockroachDB", "MariaDB",

    # Cloud Platforms
    "AWS", "Azure", "GCP", "Google Cloud", "Heroku", "Vercel", "Netlify",
    "DigitalOcean", "Linode", "Cloudflare",

    # DevOps & Infrastructure
    "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "GitHub Actions",
    "GitLab CI", "CircleCI", "ArgoCD", "Helm", "Prometheus", "Grafana",
    "Nginx", "Apache", "Traefik", "Istio", "Linux", "Unix",

    # AI / ML / Data Science
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "Pandas", "NumPy",
    "Matplotlib", "Seaborn", "Plotly", "Hugging Face", "OpenAI", "LangChain",
    "spaCy", "NLTK", "XGBoost", "LightGBM", "MLflow", "Airflow", "Spark",
    "Hadoop", "Kafka", "Flink", "Databricks", "Snowflake", "dbt",
    "Computer Vision", "NLP", "Deep Learning", "Machine Learning",
    "Reinforcement Learning", "Generative AI", "LLM", "RAG",

    # Frontend / Mobile
    "HTML", "CSS", "SASS", "SCSS", "TailwindCSS", "Bootstrap", "Material UI",
    "React Native", "Flutter", "Ionic", "Electron", "WebGL", "Three.js",
    "Redux", "Zustand", "GraphQL", "REST API", "WebSocket",

    # Testing
    "Jest", "Pytest", "Selenium", "Cypress", "Playwright", "JUnit",
    "Mocha", "Vitest", "Testing Library", "Postman",

    # Version Control & Collaboration
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence",
    "Notion", "Slack", "Trello", "Linear",

    # Security
    "OAuth", "JWT", "SSL/TLS", "OWASP", "Penetration Testing", "SIEM",
    "IAM", "Zero Trust", "SAML", "OpenID Connect",

    # Networking
    "TCP/IP", "DNS", "HTTP", "HTTPS", "gRPC", "WebRTC", "VPN", "CDN",

    # Other Tech
    "Microservices", "Serverless", "Event-Driven", "Message Queue",
    "RabbitMQ", "Apache Kafka", "Celery", "Redis Queue", "API Gateway",
    "CI/CD", "Agile", "Scrum", "Kanban", "SOLID", "Design Patterns",
    "System Design", "Distributed Systems",
]

SOFT_SKILLS = [
    "Leadership", "Communication", "Teamwork", "Problem Solving",
    "Critical Thinking", "Time Management", "Adaptability", "Creativity",
    "Collaboration", "Project Management", "Mentoring", "Presentation",
    "Negotiation", "Customer Service", "Analytical Thinking",
    "Decision Making", "Strategic Planning", "Stakeholder Management",
    "Cross-functional", "Agile", "Innovation", "Empathy", "Attention to Detail",
    "Self-motivated", "Proactive", "Detail-oriented", "Fast learner",
]

ALL_SKILLS = list(dict.fromkeys(TECH_SKILLS + SOFT_SKILLS))  # deduped

# Skill categories for visualization
SKILL_CATEGORIES = {
    "Programming": ["Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust", "Swift", "Kotlin"],
    "Web Frameworks": ["React", "Next.js", "Vue.js", "Angular", "FastAPI", "Django", "Flask", "Express.js"],
    "Databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "DynamoDB"],
    "Cloud": ["AWS", "Azure", "GCP", "Heroku", "Vercel", "Docker", "Kubernetes"],
    "AI/ML": ["TensorFlow", "PyTorch", "scikit-learn", "NLP", "Machine Learning", "Deep Learning", "LLM"],
    "DevOps": ["Docker", "Kubernetes", "CI/CD", "Jenkins", "GitHub Actions", "Terraform"],
    "Soft Skills": SOFT_SKILLS[:10],
}
