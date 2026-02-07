<template>
  <div class="skeleton-card">
    <div class="skeleton-header">
      <div class="skeleton-badge"></div>
      <div class="skeleton-actions">
        <div class="skeleton-action"></div>
        <div class="skeleton-action"></div>
      </div>
    </div>
    <div class="skeleton-title"></div>
    <div class="skeleton-description">
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
    </div>
    <div class="skeleton-tags">
      <div class="skeleton-tag"></div>
      <div class="skeleton-tag"></div>
      <div class="skeleton-tag"></div>
    </div>
    <div class="skeleton-footer">
      <div class="skeleton-author">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-name"></div>
      </div>
      <div class="skeleton-meta"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.skeleton-card {
  background: var(--bg-card, #fff);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.skeleton-badge {
  width: 60px;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-actions {
  display: flex;
  gap: 12px;
}

.skeleton-action {
  width: 40px;
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-title {
  width: 70%;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}

.skeleton-description {
  margin-bottom: 16px;
}

.skeleton-line {
  width: 100%;
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-line.short {
  width: 60%;
}

.skeleton-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.skeleton-tag {
  width: 50px;
  height: 22px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skeleton-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skeleton-avatar {
  width: 24px;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 50%;
}

.skeleton-name {
  width: 60px;
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-meta {
  width: 80px;
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 暗色模式支持 */
:root.dark .skeleton-card {
  background: var(--bg-card-dark, #1e1e1e);
}

:root.dark .skeleton-badge,
:root.dark .skeleton-action,
:root.dark .skeleton-title,
:root.dark .skeleton-line,
:root.dark .skeleton-tag,
:root.dark .skeleton-avatar,
:root.dark .skeleton-name,
:root.dark .skeleton-meta {
  background: linear-gradient(90deg, #2a2a2a 25%, #3a3a3a 50%, #2a2a2a 75%);
  background-size: 200% 100%;
}
</style>
