👋 Hi, I’m Jason—a proven Cloud Engineering & DevOps Leader with 20+ years crafting scalable, secure solutions. I enjoy mentoring and tackling challenges with IaC & AWS—check out my repos & reach out for work on projects!

#### 🛠️ I'm Currently Working on
{{range recentContributions 5}}
- [{{.Repo.Name}}]({{.Repo.URL}}) - {{.Repo.Description}} ({{humanize .OccurredAt}})
{{- end}}

#### ⭐ Recent Stars
{{range recentStars 5}}
- [{{.Repo.Name}}]({{.Repo.URL}}) - {{.Repo.Description}} ({{humanize .StarredAt}})
{{- end}}
