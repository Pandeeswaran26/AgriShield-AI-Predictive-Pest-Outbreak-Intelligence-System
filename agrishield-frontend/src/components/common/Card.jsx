export default function Card({ as: Tag = "div", className = "", children, hoverLift = false, ...props }) {
  return (
    <Tag
      className={`glass-card p-6 ${hoverLift ? "transition-transform hover:-translate-y-1" : ""} ${className}`}
      {...props}
    >
      {children}
    </Tag>
  );
}
