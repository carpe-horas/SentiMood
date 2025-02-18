import styled from 'styled-components';

const StyledButton = styled.button`
  padding: 10px 15px;
  background-color: ${(props) => props.bgColor || '#A3C6ED'};
  color: ${(props) => props.color || 'white'};
  font-size: ${(props) => props.size || '16px'};
  border: none;
  border-radius: 5px;
  transition: background 0.3s;
  
  &:hover {
    background-color: ${(props) => props.hoverColor || '#258DFB'};
  }
`;

const Button = ({ children, onClick, bgColor, color, size, hoverColor }) => {
  return (
    <StyledButton onClick={onClick} bgColor={bgColor} color={color} size={size} hoverColor={hoverColor}>
      {children}
    </StyledButton>
  );
};

export default Button;
