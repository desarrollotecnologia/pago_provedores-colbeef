import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { trackModuleFromPath } from "./tracker";

/** Instrumenta automáticamente la navegación entre módulos. */
export function usePageTracking() {
  const location = useLocation();
  const prev = useRef<string>("");

  useEffect(() => {
    const path = location.pathname;
    if (path === "/login" || path === prev.current) return;
    prev.current = path;
    trackModuleFromPath(path);
  }, [location.pathname]);
}
