interface PageHeaderProps {
  title: string;
  subtitle: string;
  greeting?: string;
}

export function PageHeader({ title, subtitle, greeting = 'Welcome back!' }: PageHeaderProps) {
  return (
    <div className="mb-5">
      <p className="text-[13px] font-600 text-royal-600">{greeting}</p>
      <h1 className="mt-1 font-display text-2xl font-800 tracking-tight text-navy-900 sm:text-[28px]">
        {title}
      </h1>
      <p className="mt-1.5 text-sm text-navy-400">{subtitle}</p>
    </div>
  );
}
