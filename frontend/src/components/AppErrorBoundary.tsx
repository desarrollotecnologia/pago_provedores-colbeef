import { Component, type ErrorInfo, type ReactNode } from "react";
import { clearSession } from "../auth/session";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export default class AppErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Error renderizando la aplicación", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="login-page">
          <div className="login-container">
            <div className="login-card">
              <h2>No se pudo cargar la pantalla</h2>
              <p>
                Actualice la página con Ctrl + F5. Si el problema continúa, cierre sesión y
                vuelva a ingresar.
              </p>
              <button
                type="button"
                className="btn btn-primary btn-block"
                onClick={() => {
                  clearSession();
                  window.location.assign("/login");
                }}
              >
                Volver al inicio de sesión
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
